import asyncio
import logging
import json
import random
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, MAX_FAILURES, WEEKLY_TEST_COUNT, TEACHER_ID
import database as db
import scheduler
from texts import t, get_fail_text, SUPPORTED_LANGS
from keyboards import (
    lang_keyboard, main_menu, next_card_keyboard, teacher_menu, timezone_keyboard,
    books_keyboard, students_picker_keyboard, manage_student_keyboard,
    admin_set_lang_keyboard, admin_set_book_keyboard, written_mode_keyboard,
    guide_menu_keyboard, guide_section_keyboard,
)
from umrah_guide import (
    SECTIONS, format_section,
    SECTION_KEYS, get_phrase, make_guide_choices, get_test_phrases, check_guide_answer,
)
from words import (
    WORDS, BOOKS_INFO,
    get_lesson_words, get_word_by_id, get_words_by_ids, make_choices, check_answer,
    check_arabic_answer, get_book_info, get_book_title, get_book_words,
    get_total_lessons, get_label,
)

logging.basicConfig(level=logging.INFO)


class S(StatesGroup):
    waiting_name = State()
    waiting_book = State()
    waiting_reminder = State()
    waiting_question = State()
    waiting_answer = State()
    waiting_broadcast = State()
    waiting_personal_msg = State()
    teacher_picking_msg = State()


# ── Helpers ────────────────────────────────────────────────────────

def user_lang(user) -> str:
    if user and user.get("lang") in SUPPORTED_LANGS:
        return user["lang"]
    return "ru"


def book_title_for(book_id: int, lang: str) -> str:
    return get_book_title(book_id, lang)


async def show_book_picker(message: Message, lang: str):
    await message.answer(t(lang, "choose_book"), reply_markup=books_keyboard(lang))


async def update_rank_and_get_delta(user_id: int):
    """Return (rank, total, delta).  delta = positive if improved, negative if dropped, 0 if same."""
    rank, total = await db.get_user_rank(user_id)
    user = await db.get_user(user_id)
    last = user.get("last_rank") if user else None
    delta = 0
    if rank is not None and last is not None:
        delta = last - rank  # smaller rank number = higher position
    if rank is not None:
        await db.update_user(user_id, last_rank=rank)
    return rank, total, delta


def format_rank_line(lang: str, rank: int, total: int, delta: int) -> str:
    if rank is None:
        return ""
    if delta > 0:
        return t(lang, "rank_up", n=delta) + "\n"
    if delta < 0:
        return t(lang, "rank_down", n=abs(delta)) + "\n"
    return t(lang, "rank_same", rank=rank, total=total) + "\n"


async def main():
    pool = await db.get_pool()
    await db.init_db(pool)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ═══════════════════════════════════════════════════════════════
    #   START / ONBOARDING
    # ═══════════════════════════════════════════════════════════════
    @dp.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        uid = message.from_user.id
        await db.create_user(uid)
        user = await db.get_user(uid)
        if uid == TEACHER_ID:
            await message.answer(t("ru", "teacher_menu"), reply_markup=teacher_menu())
            return
        if not user["name"]:
            await message.answer(t("ru", "choose_lang"), reply_markup=lang_keyboard())
        else:
            lang = user_lang(user)
            await message.answer(t(lang, "main_menu"), reply_markup=main_menu(lang))

    @dp.callback_query(lambda c: c.data and c.data.startswith("lang_") and not c.data.startswith("lang_set_"))
    async def cb_lang(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        new_lang = callback.data[5:]
        if new_lang not in SUPPORTED_LANGS:
            return
        await db.update_user(callback.from_user.id, lang=new_lang)
        user = await db.get_user(callback.from_user.id)
        if not user["name"]:
            await state.set_state(S.waiting_name)
            await callback.message.answer(t(new_lang, "ask_name"))
        else:
            await callback.message.answer(t(new_lang, "main_menu"), reply_markup=main_menu(new_lang))

    @dp.message(S.waiting_name)
    async def handle_name(message: Message, state: FSMContext):
        uid = message.from_user.id
        await db.update_user(uid, name=message.text.strip())
        user = await db.get_user(uid)
        lang = user_lang(user)
        await message.answer(t(lang, "welcome", name=user["name"]))
        await asyncio.sleep(0.5)
        await state.clear()
        await show_book_picker(message, lang)

    # ═══════════════════════════════════════════════════════════════
    #   BOOK PICKER  (open at any time — no blocking)
    # ═══════════════════════════════════════════════════════════════
    @dp.callback_query(lambda c: c.data and c.data.startswith("book_pick_"))
    async def cb_book_pick(callback: CallbackQuery):
        await callback.answer()
        try:
            book_id = int(callback.data.split("_")[2])
        except (ValueError, IndexError):
            return
        if book_id not in BOOKS_INFO:
            return
        uid = callback.from_user.id
        user = await db.get_user(uid)
        lang = user_lang(user)
        existing = user["current_book"] == book_id and user["current_lesson"] >= 1
        new_lesson = user["current_lesson"] if existing else 1
        await db.update_user(uid, current_book=book_id, current_lesson=new_lesson, state="idle")
        await db.clear_session(uid)
        info = get_book_info(book_id)
        title = info.get(f"title_{lang}") or info["title_ru"]
        await callback.message.answer(
            t(lang, "book_picked", title=title, author=info["author"], lesson=new_lesson),
            reply_markup=main_menu(lang),
        )

    # ═══════════════════════════════════════════════════════════════
    #   QUESTIONS / ANSWERS (student ↔ teacher)
    # ═══════════════════════════════════════════════════════════════
    @dp.message(S.waiting_question)
    async def handle_question(message: Message, state: FSMContext):
        uid = message.from_user.id
        user = await db.get_user(uid)
        lang = user_lang(user)
        await db.save_question(uid, message.text.strip())
        await state.clear()
        await message.answer(t(lang, "question_sent"))
        await message.bot.send_message(
            TEACHER_ID,
            f"❓ Новый вопрос от <b>{user['name']}</b>:\n\n{message.text.strip()}",
        )

    @dp.message(S.waiting_answer)
    async def handle_answer(message: Message, state: FSMContext):
        data = await state.get_data()
        qid = data["question_id"]
        await db.answer_question(qid, message.text.strip())
        question = await db.get_question_by_id(qid)
        student = await db.get_user(question["user_id"])
        slang = user_lang(student)
        await message.bot.send_message(
            question["user_id"],
            t(slang, "question_answered", answer=message.text.strip()),
        )
        await state.clear()
        await message.answer("✅ Ответ отправлен ученику.")

    @dp.message(S.waiting_broadcast)
    async def handle_broadcast(message: Message, state: FSMContext):
        users = await db.get_all_users()
        count = 0
        for u in users:
            if u["user_id"] == TEACHER_ID:
                continue
            try:
                await message.bot.send_message(u["user_id"], message.text.strip())
                count += 1
            except Exception:
                pass
        await state.clear()
        await message.answer(t("ru", "broadcast_sent", count=count))

    @dp.message(S.waiting_personal_msg)
    async def handle_personal_msg(message: Message, state: FSMContext):
        data = await state.get_data()
        target_uid = data["target_uid"]
        student = await db.get_user(target_uid)
        try:
            await message.bot.send_message(
                target_uid,
                f"📬 <b>Сообщение от учителя:</b>\n\n{message.text.strip()}",
            )
            await message.answer(
                t("ru", "personal_msg_sent", name=student["name"] or "ученик"),
            )
        except Exception as e:
            await message.answer(f"⚠️ Не удалось отправить: {e}")
        await state.clear()

    # ═══════════════════════════════════════════════════════════════
    #   REMINDER / TIMEZONE
    # ═══════════════════════════════════════════════════════════════
    @dp.message(S.waiting_reminder)
    async def handle_reminder(message: Message, state: FSMContext):
        uid = message.from_user.id
        user = await db.get_user(uid)
        lang = user_lang(user)
        try:
            h, m = message.text.strip().split(":")
            assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
            time_str = f"{int(h):02d}:{int(m):02d}"
        except Exception:
            await message.answer("⚠️ Формат: 08:00")
            return
        await db.update_user(uid, reminder_time=time_str)
        await state.clear()
        await message.answer(t(lang, "choose_timezone"), reply_markup=timezone_keyboard())

    @dp.callback_query(lambda c: c.data and c.data.startswith("tz_"))
    async def cb_timezone(callback: CallbackQuery):
        await callback.answer()
        await db.update_user(callback.from_user.id, timezone=callback.data[3:])
        user = await db.get_user(callback.from_user.id)
        await callback.message.answer(t(user_lang(user), "timezone_set"))

    # ═══════════════════════════════════════════════════════════════
    #   LESSON FLOW
    # ═══════════════════════════════════════════════════════════════
    @dp.message(Command("lesson"))
    async def cmd_lesson(message: Message):
        await start_lesson(message, message.from_user.id)

    async def start_lesson(message: Message, uid: int):
        user = await db.get_user(uid)
        lang = user_lang(user)
        book = user["current_book"]
        lesson = user["current_lesson"]
        words = get_lesson_words(lesson, book)
        if not words:
            await message.answer("⚠️ Слова не найдены для этого урока.")
            return
        await db.set_session(uid, lesson=lesson, book=book, card_index=0, word_index=0,
                             failures=0, phase="cards")
        await db.update_user(uid, state="lesson")
        await send_card(message, uid, words, 0, lang)

    async def send_card(message: Message, uid: int, words: list, idx: int, lang: str):
        if idx >= len(words):
            session = await db.get_session(uid)
            shuffled_ids = [w["id"] for w in words]
            random.shuffle(shuffled_ids)
            await db.set_session(uid, phase="visual", word_index=0,
                                 test_word_ids=json.dumps(shuffled_ids))
            await db.update_user(uid, state="quiz_visual")
            await message.answer(t(lang, "start_visual"))
            await send_visual(message, uid)
            return
        word = words[idx]
        translation = get_label(word, lang)
        await message.answer(
            t(lang, "word_card",
              current=idx + 1, total=len(words),
              ar=word["ar"], trans=word["trans"], translation=translation),
            reply_markup=next_card_keyboard(lang),
        )

    @dp.callback_query(lambda c: c.data == "next_card")
    async def cb_next_card(callback: CallbackQuery):
        await callback.answer()
        uid = callback.from_user.id
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        words = get_lesson_words(session["lesson"], session["book"])
        new_idx = session["card_index"] + 1
        await db.set_session(uid, card_index=new_idx)
        await send_card(callback.message, uid, words, new_idx, lang)

    async def send_visual(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        shuffled_ids = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(shuffled_ids):
            await db.set_session(uid, phase="await_written_choice", word_index=0)
            await db.update_user(uid, state="await_written_choice")
            await message.answer(
                t(lang, "visual_done_motivation"),
                reply_markup=written_mode_keyboard(lang),
            )
            return
        word = get_word_by_id(shuffled_ids[idx])
        if not word:
            await db.set_session(uid, word_index=idx + 1)
            await send_visual(message, uid)
            return
        book_words = get_book_words(session["book"])
        labels, _, word_ids = make_choices(word, book_words, lang)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=labels[i], callback_data=f"vis_{word['id']}_{word_ids[i]}")]
            for i in range(len(labels))
        ])
        await message.answer(
            t(lang, "visual_question", ar=word["ar"], trans=word["trans"]),
            reply_markup=kb,
        )

    @dp.callback_query(lambda c: c.data == "written_mode_translate")
    async def cb_written_mode_translate(callback: CallbackQuery):
        await callback.answer()
        uid = callback.from_user.id
        user = await db.get_user(uid)
        lang = user_lang(user)
        await db.set_session(uid, phase="written_translate", word_index=0)
        await db.update_user(uid, state="quiz_written_translate")
        await callback.message.answer(t(lang, "start_written"))
        await send_written(callback.message, uid)

    @dp.callback_query(lambda c: c.data == "written_mode_arabic")
    async def cb_written_mode_arabic(callback: CallbackQuery):
        await callback.answer()
        uid = callback.from_user.id
        user = await db.get_user(uid)
        lang = user_lang(user)
        await db.set_session(uid, phase="written_arabic", word_index=0)
        await db.update_user(uid, state="quiz_written_arabic")
        await send_written_arabic(callback.message, uid)

    @dp.callback_query(lambda c: c.data and c.data.startswith("vis_"))
    async def cb_visual(callback: CallbackQuery):
        await callback.answer()
        uid = callback.from_user.id
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        parts = callback.data.split("_")
        correct_id = int(parts[1])
        chosen_id = int(parts[2])
        correct_word = get_word_by_id(correct_id)
        if chosen_id == correct_id:
            await callback.message.answer(t(lang, "visual_correct"))
            await db.set_session(uid, word_index=session["word_index"] + 1)
            await send_visual(callback.message, uid)
        else:
            failures = session["failures"] + 1
            await db.set_session(uid, failures=failures)
            await callback.message.answer(
                t(lang, "visual_wrong", correct=get_label(correct_word, lang)),
            )
            if failures >= MAX_FAILURES:
                fresh = await db.get_user(uid)
                fi = fresh["fail_texts_index"]
                await callback.message.answer(get_fail_text(lang, fi))
                await db.update_user(uid, fail_texts_index=fi + 1)
                await db.set_session(uid, phase="cards", card_index=0, failures=0)
                await db.update_user(uid, state="lesson")
                await callback.message.answer(t(lang, "failures_visual"))
                await start_lesson(callback.message, uid)
            else:
                await send_visual(callback.message, uid)

    async def send_written(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        shuffled_ids = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(shuffled_ids):
            await finish_lesson(message, uid)
            return
        word = get_word_by_id(shuffled_ids[idx])
        if not word:
            await db.set_session(uid, word_index=idx + 1)
            await send_written(message, uid)
            return
        await message.answer(t(lang, "written_question", ar=word["ar"], trans=word["trans"]))

    async def send_written_arabic(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        shuffled_ids = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(shuffled_ids):
            await finish_lesson(message, uid)
            return
        word = get_word_by_id(shuffled_ids[idx])
        if not word:
            await db.set_session(uid, word_index=idx + 1)
            await send_written_arabic(message, uid)
            return
        translation = get_label(word, lang)
        await message.answer(t(lang, "written_arabic_question", translation=translation))

    async def finish_lesson(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        book = session["book"]
        lesson = session["lesson"]
        week = (lesson - 1) // 7 + 1
        words = get_lesson_words(lesson, book)
        for w in words:
            await db.mark_word(uid, w["id"], "learned", week, book)

        rank, total, delta = await update_rank_and_get_delta(uid)
        rank_line = format_rank_line(lang, rank, total, delta)

        await message.answer(t(lang, "lesson_passed", lesson=lesson) + (f"\n\n{rank_line}" if rank_line else ""))

        learned_this_week = await db.get_learned_words(uid, week, book)
        total_lessons = get_total_lessons(book)

        if len(learned_this_week) >= 70:
            await start_weekly_test(message, uid)
        elif lesson >= total_lessons:
            await message.answer(f"🎓 Том {book} полностью пройден! Молодец!")
            await db.update_user(uid, state="idle")
            await db.clear_session(uid)
            await show_book_picker(message, lang)
        else:
            await db.update_user(uid, current_lesson=lesson + 1, state="idle")
            await db.clear_session(uid)
            await message.answer(t(lang, "main_menu"), reply_markup=main_menu(lang))

    async def start_weekly_test(message: Message, uid: int):
        user = await db.get_user(uid)
        lang = user_lang(user)
        book = user["current_book"]
        lesson = user["current_lesson"]
        week = (lesson - 1) // 7 + 1
        learned_ids = await db.get_learned_words(uid, week, book)
        test_ids = random.sample(learned_ids, min(WEEKLY_TEST_COUNT, len(learned_ids)))
        await db.set_session(uid, phase="weekly_visual", word_index=0,
                             failures=0, test_word_ids=json.dumps(test_ids), book=book)
        await db.update_user(uid, state="weekly")
        await message.answer(t(lang, "weekly_start"))
        await send_weekly_visual(message, uid)

    async def send_weekly_visual(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        test_ids = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(test_ids):
            await db.set_session(uid, phase="weekly_written", word_index=0)
            await message.answer(t(lang, "start_written"))
            await send_weekly_written(message, uid)
            return
        words = get_words_by_ids(test_ids)
        word = words[idx]
        book_words = get_book_words(session["book"])
        labels, _, word_ids = make_choices(word, book_words, lang)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=labels[i], callback_data=f"wvis_{word['id']}_{word_ids[i]}")]
            for i in range(len(labels))
        ])
        await message.answer(
            t(lang, "visual_question", ar=word["ar"], trans=word["trans"]),
            reply_markup=kb,
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("wvis_"))
    async def cb_weekly_visual(callback: CallbackQuery):
        await callback.answer()
        uid = callback.from_user.id
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        parts = callback.data.split("_")
        correct_id = int(parts[1])
        chosen_id = int(parts[2])
        correct_word = get_word_by_id(correct_id)
        if chosen_id == correct_id:
            await callback.message.answer(t(lang, "visual_correct"))
            await db.set_session(uid, word_index=session["word_index"] + 1)
            await send_weekly_visual(callback.message, uid)
        else:
            failures = session["failures"] + 1
            await db.set_session(uid, failures=failures)
            await callback.message.answer(
                t(lang, "visual_wrong", correct=get_label(correct_word, lang)),
            )
            if failures >= MAX_FAILURES:
                fresh = await db.get_user(uid)
                fi = fresh["fail_texts_index"]
                await callback.message.answer(get_fail_text(lang, fi))
                await db.update_user(uid, fail_texts_index=fi + 1)
                await callback.message.answer(t(lang, "weekly_failed"))
                book = user["current_book"]
                lesson = user["current_lesson"]
                week = (lesson - 1) // 7 + 1
                await db.reset_week_progress(uid, week, book)
                week_start = ((lesson - 1) // 7) * 7 + 1
                await db.update_user(uid, current_lesson=week_start, state="idle")
                await db.clear_session(uid)
            else:
                await send_weekly_visual(callback.message, uid)

    async def send_weekly_written(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        test_ids = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(test_ids):
            await message.answer(t(lang, "weekly_passed"))
            next_lesson = user["current_lesson"] + 1
            total_lessons = get_total_lessons(user["current_book"])
            if next_lesson > total_lessons:
                await message.answer(f"🎓 Том {user['current_book']} полностью пройден!")
                await db.update_user(uid, state="idle")
                await db.clear_session(uid)
                await show_book_picker(message, lang)
            else:
                await db.update_user(uid, current_lesson=next_lesson, state="idle")
                await db.clear_session(uid)
                await message.answer(t(lang, "main_menu"), reply_markup=main_menu(lang))
            return
        words = get_words_by_ids(test_ids)
        word = words[idx]
        await message.answer(t(lang, "written_question", ar=word["ar"], trans=word["trans"]))

    # ═══════════════════════════════════════════════════════════════
    #   QUESTIONS — teacher answers
    # ═══════════════════════════════════════════════════════════════
    @dp.callback_query(lambda c: c.data and c.data.startswith("answer_"))
    async def cb_answer_question(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        qid = int(callback.data.split("_")[1])
        await state.update_data(question_id=qid)
        await state.set_state(S.waiting_answer)
        await callback.message.answer("✍️ Напиши ответ на вопрос:")

    # ═══════════════════════════════════════════════════════════════
    #   SETTINGS
    # ═══════════════════════════════════════════════════════════════
    @dp.callback_query(lambda c: c.data == "settings_lang")
    async def cb_settings_lang(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        user = await db.get_user(callback.from_user.id)
        await callback.message.answer(t(user_lang(user), "choose_lang"), reply_markup=lang_keyboard())

    @dp.callback_query(lambda c: c.data == "settings_name")
    async def cb_settings_name(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        user = await db.get_user(callback.from_user.id)
        await callback.message.answer(t(user_lang(user), "ask_name"))
        await state.set_state(S.waiting_name)

    @dp.callback_query(lambda c: c.data == "settings_reminder")
    async def cb_settings_reminder(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        user = await db.get_user(callback.from_user.id)
        await callback.message.answer(t(user_lang(user), "ask_reminder"))
        await state.set_state(S.waiting_reminder)

    # ═══════════════════════════════════════════════════════════════
    #   ADMIN CALLBACKS — manage individual student
    # ═══════════════════════════════════════════════════════════════
    @dp.callback_query(lambda c: c.data == "pick_cancel")
    async def cb_pick_cancel(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.edit_text("❌ Отменено.")
        await state.clear()

    @dp.callback_query(lambda c: c.data and c.data.startswith("pick_msg_"))
    async def cb_pick_msg(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        student = await db.get_user(target_uid)
        await state.update_data(target_uid=target_uid)
        await state.set_state(S.waiting_personal_msg)
        await callback.message.answer(
            t("ru", "ask_personal_msg", name=student["name"] or "ученик"),
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("pick_manage_"))
    async def cb_pick_manage(callback: CallbackQuery):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        student = await db.get_user(target_uid)
        if not student:
            await callback.message.answer("Ученик не найден.")
            return
        await callback.message.answer(
            f"🛠 Управление: <b>{student['name']}</b>\n\n"
            f"📚 Том {student['current_book']}, Урок {student['current_lesson']}\n"
            f"🌐 Язык: {student['lang']}",
            reply_markup=manage_student_keyboard(target_uid),
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("adm_msg_"))
    async def cb_adm_msg(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        student = await db.get_user(target_uid)
        await state.update_data(target_uid=target_uid)
        await state.set_state(S.waiting_personal_msg)
        await callback.message.answer(
            t("ru", "ask_personal_msg", name=student["name"] or "ученик"),
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("adm_lang_"))
    async def cb_adm_lang(callback: CallbackQuery):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        await callback.message.answer(
            "Выбери новый язык бота для ученика:",
            reply_markup=admin_set_lang_keyboard(target_uid),
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("set_lang_"))
    async def cb_set_lang(callback: CallbackQuery):
        await callback.answer()
        parts = callback.data.split("_")
        target_uid, lang = int(parts[2]), parts[3]
        if lang not in SUPPORTED_LANGS:
            return
        await db.update_user(target_uid, lang=lang)
        student = await db.get_user(target_uid)
        await callback.message.answer(f"✅ Язык ученика <b>{student['name']}</b> установлен: {lang}")

    @dp.callback_query(lambda c: c.data and c.data.startswith("adm_book_"))
    async def cb_adm_book(callback: CallbackQuery):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        await callback.message.answer(
            "Выбери новый том для ученика:",
            reply_markup=admin_set_book_keyboard(target_uid),
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("set_book_"))
    async def cb_set_book(callback: CallbackQuery):
        await callback.answer()
        parts = callback.data.split("_")
        target_uid, book_id = int(parts[2]), int(parts[3])
        await db.update_user(target_uid, current_book=book_id, current_lesson=1, state="idle")
        await db.clear_session(target_uid)
        student = await db.get_user(target_uid)
        await callback.message.answer(
            f"✅ Ученик <b>{student['name']}</b> переведён в Том {book_id}, Урок 1.",
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("adm_reset_"))
    async def cb_adm_reset(callback: CallbackQuery):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        await db.reset_all_progress(target_uid)
        student = await db.get_user(target_uid)
        await callback.message.answer(
            f"🔄 Прогресс ученика <b>{student['name']}</b> сброшен. Начинает с Тома 1, Урок 1.",
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("adm_stat_"))
    async def cb_adm_stat(callback: CallbackQuery):
        await callback.answer()
        target_uid = int(callback.data.split("_")[2])
        student = await db.get_user(target_uid)
        learned = await db.get_total_learned_words(target_uid)
        rank, total = await db.get_user_rank(target_uid)
        book_learned = len(await db.get_learned_words_in_book(target_uid, student["current_book"]))
        book_total = len(get_book_words(student["current_book"]))
        await callback.message.answer(
            f"📊 <b>{student['name']}</b>\n\n"
            f"📖 Том: {student['current_book']} ({book_learned}/{book_total})\n"
            f"📚 Урок: {student['current_lesson']}\n"
            f"✅ Всего слов: {learned}\n"
            f"🏆 Рейтинг: #{rank} из {total}\n"
            f"🌐 Язык: {student['lang']}\n"
            f"⏰ Уведомления: {student['reminder_time'] or 'не настроены'}",
        )

    # ═══════════════════════════════════════════════════════════════
    #   UMRAH GUIDE
    # ═══════════════════════════════════════════════════════════════
    @dp.callback_query(lambda c: c.data and c.data.startswith("guide_")
                       and not c.data.startswith("guide_test_"))
    async def cb_guide_section(call: CallbackQuery):
        key = call.data[len("guide_"):]
        if key not in SECTIONS:
            await call.answer()
            return
        user = await db.get_user(call.from_user.id)
        lang = user_lang(user)
        text = format_section(key, lang)
        await call.message.answer(text, parse_mode="HTML",
                                  reply_markup=guide_section_keyboard(key, lang))
        await call.answer()

    @dp.callback_query(lambda c: c.data and c.data.startswith("guide_test_"))
    async def cb_guide_test_start(call: CallbackQuery):
        await call.answer()
        uid = call.from_user.id
        user = await db.get_user(uid)
        lang = user_lang(user)
        section_key = call.data[len("guide_test_"):]
        if section_key not in SECTIONS:
            return
        test_refs = get_test_phrases(section_key, count=10)
        await db.set_session(uid, lesson=0, book=0, card_index=0, word_index=0,
                             failures=0, phase="guide_visual",
                             test_word_ids=json.dumps(test_refs))
        await db.update_user(uid, state="guide_visual")
        await call.message.answer(t(lang, "guide_visual_start"))
        await send_guide_visual(call.message, uid)

    async def send_guide_visual(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        test_refs = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(test_refs):
            await db.set_session(uid, phase="guide_written", word_index=0, failures=0)
            await db.update_user(uid, state="guide_written")
            await message.answer(t(lang, "guide_visual_done"))
            await send_guide_written(message, uid)
            return
        sec_idx, ph_idx = test_refs[idx]
        phrase = get_phrase(sec_idx, ph_idx)
        choices = make_guide_choices(sec_idx, ph_idx)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=get_phrase(cs, cp).get(lang, get_phrase(cs, cp)["ru"]),
                callback_data=f"gv_{sec_idx}_{ph_idx}_{cs}_{cp}",
            )]
            for cs, cp in choices
        ])
        await message.answer(
            f"{t(lang, 'guide_what_means')}\n\n<blockquote><b>{phrase['ar']}</b></blockquote>\n\n📢 <i>{phrase['trans']}</i>",
            parse_mode="HTML",
            reply_markup=kb,
        )

    @dp.callback_query(lambda c: c.data and c.data.startswith("gv_"))
    async def cb_guide_visual(callback: CallbackQuery):
        await callback.answer()
        uid = callback.from_user.id
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        if not session:
            return
        lang = user_lang(user)
        parts = callback.data.split("_")
        correct_sec, correct_ph = int(parts[1]), int(parts[2])
        chosen_sec, chosen_ph = int(parts[3]), int(parts[4])
        correct_phrase = get_phrase(correct_sec, correct_ph)
        if (chosen_sec, chosen_ph) == (correct_sec, correct_ph):
            await callback.message.answer(t(lang, "guide_correct"))
            await db.set_session(uid, word_index=session["word_index"] + 1)
            await send_guide_visual(callback.message, uid)
        else:
            failures = session["failures"] + 1
            await db.set_session(uid, failures=failures)
            await callback.message.answer(
                t(lang, "guide_wrong", correct=correct_phrase.get(lang, correct_phrase["ru"])),
                parse_mode="HTML",
            )
            if failures >= MAX_FAILURES:
                fresh = await db.get_user(uid)
                fi = fresh["fail_texts_index"]
                await callback.message.answer(get_fail_text(lang, fi))
                await db.update_user(uid, fail_texts_index=fi + 1)
                test_refs = json.loads(session["test_word_ids"] or "[]")
                random.shuffle(test_refs)
                await db.set_session(uid, word_index=0, failures=0,
                                     test_word_ids=json.dumps(test_refs))
                await callback.message.answer(t(lang, "guide_restart_test"))
                await send_guide_visual(callback.message, uid)
            else:
                await send_guide_visual(callback.message, uid)

    async def send_guide_written(message: Message, uid: int):
        user = await db.get_user(uid)
        session = await db.get_session(uid)
        lang = user_lang(user)
        test_refs = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        if idx >= len(test_refs):
            await db.update_user(uid, state="idle")
            await db.clear_session(uid)
            await message.answer(t(lang, "guide_done"), reply_markup=main_menu(lang))
            return
        sec_idx, ph_idx = test_refs[idx]
        phrase = get_phrase(sec_idx, ph_idx)
        await message.answer(
            f"{t(lang, 'guide_translate')}\n\n<blockquote><b>{phrase['ar']}</b></blockquote>\n\n📢 <i>{phrase['trans']}</i>",
            parse_mode="HTML",
        )

    # ═══════════════════════════════════════════════════════════════
    #   GLOBAL TEXT HANDLER (menu buttons)
    # ═══════════════════════════════════════════════════════════════
    @dp.message()
    async def global_text_handler(message: Message, state: FSMContext):
        if not message.text or message.text.startswith("/"):
            return
        current_state = await state.get_state()
        if current_state is not None:
            return
        uid = message.from_user.id
        user = await db.get_user(uid)
        if not user:
            return

        # ── Teacher actions ──
        if uid == TEACHER_ID:
            txt = message.text
            if txt == "👥 Мои ученики":
                students = await db.get_students_sorted()
                if not students:
                    await message.answer(t("ru", "students_empty"))
                    return
                text = t("ru", "students_header", count=len(students))
                for i, s in enumerate(students, 1):
                    book = s["current_book"]
                    text += (
                        f"{i}. <b>{s['name'] or '—'}</b> · "
                        f"Том {book}, Урок {s['current_lesson']} · "
                        f"{s['learned']} слов\n"
                    )
                await message.answer(text)
                return
            if txt == "😴 Лентяи":
                lazy = await db.get_lazy_students()
                if not lazy:
                    await message.answer(t("ru", "no_lazy"))
                    return
                lines = "\n".join(f"• {s['name'] or '—'}" for s in lazy)
                await message.answer(t("ru", "lazy_students", list=lines))
                return
            if txt == "📬 Вопросы учеников":
                questions = await db.get_unanswered_questions()
                if not questions:
                    await message.answer(t("ru", "no_questions"))
                    return
                for q in questions:
                    kb = InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="✍️ Ответить", callback_data=f"answer_{q['id']}"),
                    ]])
                    await message.answer(f"❓ <b>{q['name']}</b>:\n{q['text']}", reply_markup=kb)
                return
            if txt == "📊 Полная статистика":
                students = await db.get_students_sorted()
                total_users = len(students)
                total_words_learned = sum(s["learned"] for s in students)
                avg = total_words_learned / total_users if total_users else 0
                lazy_count = sum(1 for s in students if s["learned"] == 0)
                book_stats = {1: 0, 2: 0, 3: 0}
                for s in students:
                    book_stats[s["current_book"]] = book_stats.get(s["current_book"], 0) + 1
                await message.answer(
                    f"📊 <b>Полная статистика</b>\n\n"
                    f"👥 Учеников: {total_users}\n"
                    f"📚 Всего слов выучено: {total_words_learned}\n"
                    f"📈 В среднем: {avg:.1f} слов/ученик\n"
                    f"😴 Лентяев (0 слов): {lazy_count}\n\n"
                    f"📖 Распределение по томам:\n"
                    f"  Том 1: {book_stats.get(1, 0)} учеников\n"
                    f"  Том 2: {book_stats.get(2, 0)} учеников\n"
                    f"  Том 3: {book_stats.get(3, 0)} учеников"
                )
                return
            if txt == "✉️ Личное сообщение":
                students = await db.get_students_sorted()
                if not students:
                    await message.answer(t("ru", "students_empty"))
                    return
                await message.answer(
                    "Кому отправить сообщение?",
                    reply_markup=students_picker_keyboard(students, "msg"),
                )
                return
            if txt == "📢 Рассылка всем":
                await message.answer(t("ru", "ask_broadcast"))
                await state.set_state(S.waiting_broadcast)
                return
            if txt == "🛠 Управление учеником":
                students = await db.get_students_sorted()
                if not students:
                    await message.answer(t("ru", "students_empty"))
                    return
                await message.answer(
                    "Кем будем управлять?",
                    reply_markup=students_picker_keyboard(students, "manage"),
                )
                return
            return

        # ── Student actions ──
        lang = user_lang(user)
        if message.text == t(lang, "btn_lesson"):
            await start_lesson(message, uid)
            return
        if message.text == t(lang, "btn_books"):
            await show_book_picker(message, lang)
            return
        if message.text == t(lang, "btn_profile"):
            book = user["current_book"]
            lesson = user["current_lesson"]
            book_learned = len(await db.get_learned_words_in_book(uid, book))
            book_total = len(get_book_words(book))
            total_learned = await db.get_total_learned_words(uid)
            rank, total_students = await db.get_user_rank(uid)
            info = get_book_info(book)
            book_title_loc = info.get(f"title_{lang}") or info["title_ru"]
            rank_text = ""
            if rank is not None:
                rank_text = t(lang, "rank_same", rank=rank, total=total_students) + "\n"
            await message.answer(
                f"👤 <b>{user['name']}</b>\n\n"
                f"📖 {book_title_loc}\n"
                f"👤 {info['author']}\n"
                f"📚 Урок {lesson} из {get_total_lessons(book)}\n"
                f"✅ Всего выучено: {total_learned} слов\n"
                f"📊 В этом томе: {book_learned}/{book_total}\n"
                f"{rank_text}"
                f"🌐 Язык: {lang}"
            )
            return
        if message.text == t(lang, "btn_stats"):
            book = user["current_book"]
            lesson = user["current_lesson"]
            book_learned = len(await db.get_learned_words_in_book(uid, book))
            book_total = len(get_book_words(book))
            total_learned = await db.get_total_learned_words(uid)
            rank, total_students = await db.get_user_rank(uid)
            info = get_book_info(book)
            book_title_loc = info.get(f"title_{lang}") or info["title_ru"]
            rank_text = ""
            if rank is not None:
                rank_text = t(lang, "rank_same", rank=rank, total=total_students) + "\n"
            await message.answer(t(lang, "stats_text",
                book_title=book_title_loc,
                lesson=lesson,
                total_lessons=get_total_lessons(book),
                total_learned=total_learned,
                book_learned=book_learned,
                book_total=book_total,
                rank_text=rank_text,
            ))
            return
        if message.text == t(lang, "btn_ask"):
            await message.answer(t(lang, "ask_question"))
            await state.set_state(S.waiting_question)
            return
        if message.text == t(lang, "btn_settings"):
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Изменить язык", callback_data="settings_lang")],
                [InlineKeyboardButton(text="✏️ Изменить имя", callback_data="settings_name")],
                [InlineKeyboardButton(text="⏰ Уведомление", callback_data="settings_reminder")],
            ])
            await message.answer("⚙️ Настройки:", reply_markup=kb)
            return
        if message.text == t(lang, "btn_guide"):
            await message.answer(t(lang, "guide_choose"), reply_markup=guide_menu_keyboard(lang))
            return

        # ── Quiz answers (written test) ──
        session = await db.get_session(uid)
        if not session:
            return
        state_val = user["state"]
        phase = session["phase"]

        if state_val == "quiz_written_translate" and phase == "written_translate":
            shuffled_ids = json.loads(session["test_word_ids"] or "[]")
            idx = session["word_index"]
            if idx >= len(shuffled_ids):
                return
            word = get_word_by_id(shuffled_ids[idx])
            if not word:
                await db.set_session(uid, word_index=idx + 1)
                await send_written(message, uid)
                return
            if check_answer(message.text, word):
                await message.answer(t(lang, "written_correct"))
                await db.set_session(uid, word_index=idx + 1)
                await send_written(message, uid)
            else:
                failures = session["failures"] + 1
                await db.set_session(uid, failures=failures)
                await message.answer(t(lang, "written_wrong", correct=get_label(word, lang)))
                if failures >= MAX_FAILURES:
                    fresh = await db.get_user(uid)
                    fi = fresh["fail_texts_index"]
                    await message.answer(get_fail_text(lang, fi))
                    await db.update_user(uid, fail_texts_index=fi + 1)
                    new_shuffle = list(shuffled_ids); random.shuffle(new_shuffle)
                    await db.set_session(uid, phase="visual", word_index=0, failures=0,
                                         test_word_ids=json.dumps(new_shuffle))
                    await db.update_user(uid, state="quiz_visual")
                    await message.answer(t(lang, "failures_written"))
                    await send_visual(message, uid)
                else:
                    await send_written(message, uid)
            return

        if state_val == "quiz_written_arabic" and phase == "written_arabic":
            shuffled_ids = json.loads(session["test_word_ids"] or "[]")
            idx = session["word_index"]
            if idx >= len(shuffled_ids):
                return
            word = get_word_by_id(shuffled_ids[idx])
            if not word:
                await db.set_session(uid, word_index=idx + 1)
                await send_written_arabic(message, uid)
                return
            if check_arabic_answer(message.text, word):
                await message.answer(t(lang, "arabic_correct"))
                await db.set_session(uid, word_index=idx + 1)
                await send_written_arabic(message, uid)
            else:
                failures = session["failures"] + 1
                await db.set_session(uid, failures=failures)
                await message.answer(t(lang, "arabic_wrong", correct=word["ar"]))
                if failures >= MAX_FAILURES:
                    fresh = await db.get_user(uid)
                    fi = fresh["fail_texts_index"]
                    await message.answer(get_fail_text(lang, fi))
                    await db.update_user(uid, fail_texts_index=fi + 1)
                    new_shuffle = list(shuffled_ids); random.shuffle(new_shuffle)
                    await db.set_session(uid, phase="visual", word_index=0, failures=0,
                                         test_word_ids=json.dumps(new_shuffle))
                    await db.update_user(uid, state="quiz_visual")
                    await message.answer(t(lang, "failures_written"))
                    await send_visual(message, uid)
                else:
                    await send_written_arabic(message, uid)
            return

        if state_val == "weekly" and phase == "weekly_written":
            test_ids = json.loads(session["test_word_ids"] or "[]")
            idx = session["word_index"]
            words = get_words_by_ids(test_ids)
            if idx >= len(words):
                return
            word = words[idx]
            if check_answer(message.text, word):
                await message.answer(t(lang, "written_correct"))
                await db.set_session(uid, word_index=idx + 1)
                await send_weekly_written(message, uid)
            else:
                failures = session["failures"] + 1
                await db.set_session(uid, failures=failures)
                await message.answer(t(lang, "written_wrong", correct=get_label(word, lang)))
                if failures >= MAX_FAILURES:
                    fresh = await db.get_user(uid)
                    fi = fresh["fail_texts_index"]
                    await message.answer(get_fail_text(lang, fi))
                    await db.update_user(uid, fail_texts_index=fi + 1)
                    await message.answer(t(lang, "weekly_failed"))
                    book = user["current_book"]
                    lesson = user["current_lesson"]
                    week = (lesson - 1) // 7 + 1
                    await db.reset_week_progress(uid, week, book)
                    week_start = ((lesson - 1) // 7) * 7 + 1
                    await db.update_user(uid, current_lesson=week_start, state="idle")
                    await db.clear_session(uid)
            return

        if state_val == "guide_written" and phase == "guide_written":
            test_refs = json.loads(session["test_word_ids"] or "[]")
            idx = session["word_index"]
            if idx >= len(test_refs):
                return
            sec_idx, ph_idx = test_refs[idx]
            phrase = get_phrase(sec_idx, ph_idx)
            if check_guide_answer(message.text, phrase, lang):
                await message.answer(t(lang, "guide_correct"))
                await db.set_session(uid, word_index=idx + 1)
                await send_guide_written(message, uid)
            else:
                failures = session["failures"] + 1
                await db.set_session(uid, failures=failures)
                await message.answer(
                    t(lang, "guide_wrong", correct=phrase.get(lang, phrase["ru"])),
                    parse_mode="HTML",
                )
                if failures >= MAX_FAILURES:
                    fresh = await db.get_user(uid)
                    fi = fresh["fail_texts_index"]
                    await message.answer(get_fail_text(lang, fi))
                    await db.update_user(uid, fail_texts_index=fi + 1)
                    test_refs_copy = list(test_refs)
                    random.shuffle(test_refs_copy)
                    await db.set_session(uid, phase="guide_visual", word_index=0,
                                         failures=0, test_word_ids=json.dumps(test_refs_copy))
                    await db.update_user(uid, state="guide_visual")
                    await message.answer(t(lang, "guide_restart_visual"))
                    await send_guide_visual(message, uid)
                else:
                    await send_guide_written(message, uid)
            return

    # ───────────────────────────────────────────────────────────────
    # Start: delete webhook → scheduler → polling + API server
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler.setup(bot)

    # API server runs as a separate process (see Procfile)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
