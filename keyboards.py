import os
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
)
from texts import t
from umrah_guide import SECTIONS


def lang_keyboard() -> InlineKeyboardMarkup:
    """4 languages: RU, TJ, EN, UZ — 2 rows of 2."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇹🇯 Тоҷикӣ",  callback_data="lang_tj"),
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English",  callback_data="lang_en"),
            InlineKeyboardButton(text="🇺🇿 Oʻzbek",   callback_data="lang_uz"),
        ],
    ])


MINIAPP_URL_DEFAULT = "https://repository-name-arabic-path-miniapp.vercel.app"

def main_menu(lang: str) -> ReplyKeyboardMarkup:
    miniapp_url = os.getenv("MINIAPP_URL", MINIAPP_URL_DEFAULT)
    if miniapp_url:
        rows = [[
            KeyboardButton(
                text=t(lang, "btn_miniapp"),
                web_app=WebAppInfo(url=miniapp_url),
            )
        ]]
    else:
        rows = [
            [KeyboardButton(text=t(lang, "btn_lesson")), KeyboardButton(text=t(lang, "btn_profile"))],
            [KeyboardButton(text=t(lang, "btn_stats")),  KeyboardButton(text=t(lang, "btn_books"))],
            [KeyboardButton(text=t(lang, "btn_ask")),    KeyboardButton(text=t(lang, "btn_settings"))],
            [KeyboardButton(text=t(lang, "btn_guide"))],
        ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def guide_section_keyboard(section_key: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "btn_guide_test"), callback_data=f"guide_test_{section_key}"),
    ]])


def guide_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """8-section Umrah phrasebook menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{sec['emoji']} {sec.get(f'title_{lang}', sec['title_ru'])}",
            callback_data=f"guide_{key}",
        )]
        for key, sec in SECTIONS.items()
    ])


def next_card_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "btn_next"), callback_data="next_card"),
    ]])


def lesson_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "btn_learned"), callback_data="lesson_learned"),
        InlineKeyboardButton(text=t(lang, "btn_repeat"),  callback_data="lesson_repeat"),
    ]])


def written_mode_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Pick written-test mode: type translation OR type Arabic."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_write_translation"), callback_data="written_mode_translate")],
        [InlineKeyboardButton(text=t(lang, "btn_write_arabic"),      callback_data="written_mode_arabic")],
    ])


def books_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Pick a volume. Title on first line, author on second line below."""
    from words import BOOKS_INFO
    rows = []
    for book_id in sorted(BOOKS_INFO.keys()):
        info = BOOKS_INFO[book_id]
        title = info.get(f"title_{lang}") or info["title_ru"]
        emoji = info.get("level_emoji", "📖")
        # Author shown on the same button on next line (using \n which Telegram preserves on inline)
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {title}\n👤 {info['author']}",
            callback_data=f"book_pick_{book_id}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def teacher_menu() -> ReplyKeyboardMarkup:
    miniapp_url = os.getenv("MINIAPP_URL", MINIAPP_URL_DEFAULT)
    if miniapp_url:
        keyboard = [[
            KeyboardButton(
                text="🌐 Открыть Mini App",
                web_app=WebAppInfo(url=miniapp_url),
            )
        ]]
    else:
        keyboard = [
            [KeyboardButton(text="👥 Мои ученики"),     KeyboardButton(text="😴 Лентяи")],
            [KeyboardButton(text="📬 Вопросы учеников"), KeyboardButton(text="📊 Полная статистика")],
            [KeyboardButton(text="✉️ Личное сообщение"), KeyboardButton(text="📢 Рассылка всем")],
            [KeyboardButton(text="🛠 Управление учеником")],
        ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def students_picker_keyboard(students: list, action: str) -> InlineKeyboardMarkup:
    """Pick a student. `action` is included in callback so handlers can route.
    Layout: 1 student per row showing name + progress.
    """
    rows = []
    for s in students:
        learned = s.get("learned", 0)
        name = s.get("name") or "—"
        rows.append([InlineKeyboardButton(
            text=f"{name} · {learned} слов",
            callback_data=f"pick_{action}_{s['user_id']}",
        )])
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="pick_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def manage_student_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin actions for a specific student."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Сменить язык бота",   callback_data=f"adm_lang_{user_id}")],
        [InlineKeyboardButton(text="📖 Сменить том",         callback_data=f"adm_book_{user_id}")],
        [InlineKeyboardButton(text="🔄 Сброс прогресса",     callback_data=f"adm_reset_{user_id}")],
        [InlineKeyboardButton(text="✉️ Личное сообщение",    callback_data=f"adm_msg_{user_id}")],
        [InlineKeyboardButton(text="📊 Подробная статистика", callback_data=f"adm_stat_{user_id}")],
        [InlineKeyboardButton(text="❌ Отмена",              callback_data="pick_cancel")],
    ])


def admin_set_lang_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 RU", callback_data=f"set_lang_{user_id}_ru"),
            InlineKeyboardButton(text="🇹🇯 TJ", callback_data=f"set_lang_{user_id}_tj"),
        ],
        [
            InlineKeyboardButton(text="🇬🇧 EN", callback_data=f"set_lang_{user_id}_en"),
            InlineKeyboardButton(text="🇺🇿 UZ", callback_data=f"set_lang_{user_id}_uz"),
        ],
    ])


def admin_set_book_keyboard(user_id: int) -> InlineKeyboardMarkup:
    from words import BOOKS_INFO
    rows = []
    for book_id in sorted(BOOKS_INFO.keys()):
        info = BOOKS_INFO[book_id]
        rows.append([InlineKeyboardButton(
            text=f"{info.get('level_emoji','📖')} {info['title_ru']}",
            callback_data=f"set_book_{user_id}_{book_id}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def timezone_keyboard() -> InlineKeyboardMarkup:
    timezones = [
        ("🕌 Мекка / Медина", "Asia/Riyadh"),
        ("🇷🇺 Москва", "Europe/Moscow"),
        ("🇷🇺 Екатеринбург", "Asia/Yekaterinburg"),
        ("🇷🇺 Новосибирск", "Asia/Novosibirsk"),
        ("🇹🇯 Душанбе", "Asia/Dushanbe"),
        ("🇺🇿 Ташкент", "Asia/Tashkent"),
        ("🇰🇿 Алматы", "Asia/Almaty"),
        ("🇦🇿 Баку", "Asia/Baku"),
        ("🇦🇪 Дубай", "Asia/Dubai"),
        ("🇹🇷 Стамбул", "Europe/Istanbul"),
        ("🇩🇪 Берлин", "Europe/Berlin"),
        ("🇬🇧 Лондон", "Europe/London"),
        ("🇺🇸 Нью-Йорк", "America/New_York"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"tz_{tz}")]
        for name, tz in timezones
    ])
