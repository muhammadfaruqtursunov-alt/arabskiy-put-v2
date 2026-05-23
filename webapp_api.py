# -*- coding: utf-8 -*-
"""
FastAPI backend for Arabic Path Telegram Mini App.
Runs alongside aiogram polling — started by bot.py via uvicorn.
Authentication: Telegram initData HMAC-SHA256 (standard TWA).
"""

import hashlib
import hmac
import json
import random
import urllib.parse
import urllib.request as _urllib_req
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from config import BOT_TOKEN, MAX_FAILURES, TEACHER_ID
import database as db
from words import (
    BOOKS_INFO, get_lesson_words, get_word_by_id, get_words_by_ids,
    get_book_words, get_total_lessons, make_choices, check_answer,
    check_arabic_answer, get_label, get_book_info,
)
from umrah_guide import (
    SECTIONS, SECTION_KEYS, get_phrase, make_guide_choices,
    get_test_phrases, check_guide_answer, format_section,
)


# ── Auth ────────────────────────────────────────────────────────────

def validate_init_data(init_data: str) -> dict:
    """Validate Telegram WebApp initData using HMAC-SHA256.
    Returns parsed user dict or raises HTTPException 401."""
    parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash")

    data_check = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, received_hash):
        raise HTTPException(status_code=401, detail="Invalid initData")

    user_json = parsed.get("user", "{}")
    try:
        return json.loads(user_json)
    except Exception:
        raise HTTPException(status_code=401, detail="Cannot parse user")


async def get_current_user(x_init_data: str = Header(..., alias="X-Init-Data")):
    """Dependency: validate initData header, update streak, return DB user row."""
    if db._pool is None:
        raise HTTPException(status_code=503, detail="Database not ready yet, retry in a moment")
    tg_user = validate_init_data(x_init_data)
    uid = tg_user.get("id")
    if not uid:
        raise HTTPException(status_code=401, detail="No user id")
    try:
        await db.update_streak(uid)
    except Exception:
        pass  # non-critical — don't block login if streak columns missing
    user = await db.get_user(uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Models ──────────────────────────────────────────────────────────

class CreateUserBody(BaseModel):
    name: str
    lang: str = "ru"
    tg_id: int  # frontend sends tg_id (from initData) + name/lang


class UpdateLangBody(BaseModel):
    lang: str


class UpdateNameBody(BaseModel):
    name: str


class QuizStartBody(BaseModel):
    book: int
    lesson: int
    mode: str = "visual"  # "visual" | "written" | "arabic"


class QuizAnswerBody(BaseModel):
    word_id: int         # correct word id (from question)
    chosen_id: int       # word id user picked (visual) or -1 (written)
    typed: Optional[str] = None  # user typed answer (written/arabic modes)
    mode: str = "visual"


class UmrahQuizStartBody(BaseModel):
    section_key: str
    count: int = 10


class UmrahQuizAnswerBody(BaseModel):
    # encoded as "sec_idx:ph_idx"
    correct_ref: str
    chosen_ref: Optional[str] = None   # visual mode
    typed: Optional[str] = None        # written mode
    mode: str = "visual"
    lang: str = "ru"


class AskQuestionBody(BaseModel):
    question: str


class AnswerBody(BaseModel):
    answer: str


class BroadcastBody(BaseModel):
    message: str


class PersonalMessageBody(BaseModel):
    user_id: int
    message: str


class BgConfigBody(BaseModel):
    bg_url: str


class ReminderBody(BaseModel):
    reminder_time: Optional[str] = None   # "HH:MM" or null to disable
    timezone: str = "Europe/Moscow"


class SessionBody(BaseModel):
    seconds: int  # duration of the app session in seconds


# ── Factory ─────────────────────────────────────────────────────────

def create_app(pool=None, lifespan=None) -> FastAPI:
    """Create FastAPI app. DB pool is set via db._pool (by caller or lifespan)."""
    if pool is not None:
        db._pool = pool
    # Note: if pool is None, db._pool must be set before any requests arrive

    app = FastAPI(title="Arabic Path Mini App API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-Init-Data", "Authorization"],
        expose_headers=["*"],
    )

    # ── TTS proxy (no auth) ─────────────────────────────────────────

    @app.get("/api/tts")
    def tts_proxy(text: str):
        if not text or len(text) > 300:
            raise HTTPException(status_code=400, detail="invalid text")
        url = (
            "https://translate.google.com/translate_tts"
            f"?ie=UTF-8&q={urllib.parse.quote(text)}&tl=ar&client=tw-ob"
        )
        req = _urllib_req.Request(url, headers={
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36"
            ),
            "Referer": "https://translate.google.com/",
        })
        try:
            with _urllib_req.urlopen(req, timeout=8) as resp:
                audio = resp.read()
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        return Response(
            content=audio,
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    # ── Health / debug (no auth) ─────────────────────────────────────

    @app.get("/api/webapp/health")
    async def health():
        return {"ok": True, "service": "arabic-path-miniapp"}

    @app.get("/api/webapp/debug")
    async def debug(request: Request):
        raw = request.headers.get("x-init-data", "")
        return {
            "has_init_data": bool(raw),
            "length": len(raw),
            "preview": raw[:40] if raw else "",
        }

    # ── User endpoints ───────────────────────────────────────────────

    @app.get("/api/webapp/user")
    async def get_user_profile(user=Depends(get_current_user)):
        """Profile + progress for Mini App home screen."""
        uid = user["user_id"]
        total_learned = await db.get_total_learned_words(uid)
        rank, total_students = await db.get_user_rank(uid)
        book = user["current_book"]
        book_info = get_book_info(book)
        book_learned = len(await db.get_learned_words_in_book(uid, book))
        book_total = len(get_book_words(book))
        return {
            "user_id": uid,
            "name": user["name"] or "",
            "lang": user["lang"] or "ru",
            "is_teacher": (uid == TEACHER_ID),
            "current_book": book,
            "current_lesson": user["current_lesson"],
            "streak": user["streak"] or 0,
            "total_learned": total_learned,
            "rank": rank,
            "total_students": total_students,
            "book_info": {
                "title_ru": book_info["title_ru"],
                "title_tj": book_info["title_tj"],
                "title_en": book_info["title_en"],
                "author": book_info["author"],
                "level_emoji": book_info["level_emoji"],
                "total_lessons": get_total_lessons(book),
            },
            "book_progress": {
                "learned": book_learned,
                "total": book_total,
                "pct": round(book_learned / book_total * 100) if book_total else 0,
            },
        }

    @app.post("/api/webapp/user", status_code=201)
    async def create_user(body: CreateUserBody,
                          x_init_data: str = Header(..., alias="X-Init-Data")):
        """Onboarding: create user with name + lang."""
        if db._pool is None:
            raise HTTPException(status_code=503, detail="Database not ready yet, retry in a moment")
        tg_user = validate_init_data(x_init_data)
        uid = tg_user.get("id")
        if not uid:
            raise HTTPException(status_code=401, detail="No user id")
        await db.create_user(uid)
        safe_lang = body.lang if body.lang in ("ru", "tj", "en", "ar", "uz") else "ru"
        await db.update_user(uid, name=body.name.strip(), lang=safe_lang)
        await db.update_streak(uid)
        user = await db.get_user(uid)
        return {"ok": True, "name": user["name"], "lang": user["lang"]}

    @app.put("/api/webapp/user/lang")
    async def set_lang(body: UpdateLangBody, user=Depends(get_current_user)):
        safe_lang = body.lang if body.lang in ("ru", "tj", "en", "ar", "uz") else "ru"
        await db.update_user(user["user_id"], lang=safe_lang)
        return {"ok": True, "lang": safe_lang}

    @app.put("/api/webapp/user/name")
    async def set_name(body: UpdateNameBody, user=Depends(get_current_user)):
        name = body.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        await db.update_user(user["user_id"], name=name)
        return {"ok": True, "name": name}

    @app.post("/api/webapp/user/session")
    async def log_session(body: SessionBody, user=Depends(get_current_user)):
        """Record how many seconds the user spent in the app this session."""
        await db.add_session_time(user["user_id"], body.seconds)
        return {"ok": True}

    @app.get("/api/webapp/user/reminder")
    async def get_reminder(user=Depends(get_current_user)):
        """Return user's current reminder time and timezone."""
        return {
            "reminder_time": user.get("reminder_time"),
            "timezone": user.get("timezone") or "Europe/Moscow",
        }

    @app.put("/api/webapp/user/reminder")
    async def set_reminder(body: ReminderBody, user=Depends(get_current_user)):
        """Save reminder time + timezone. Set reminder_time=null to disable."""
        import pytz, re
        # Validate / sanitise timezone
        tz_name = body.timezone or "Europe/Moscow"
        try:
            pytz.timezone(tz_name)
        except Exception:
            tz_name = "Europe/Moscow"
        # Validate time format HH:MM
        rt = body.reminder_time
        if rt:
            rt = rt.strip()
            if not re.match(r"^\d{2}:\d{2}$", rt):
                raise HTTPException(status_code=400, detail="Time must be HH:MM")
        await db.update_user(user["user_id"], reminder_time=rt, timezone=tz_name)
        return {"ok": True, "reminder_time": rt, "timezone": tz_name}

    # ── Volumes & Lessons ────────────────────────────────────────────

    @app.get("/api/webapp/volumes")
    async def get_volumes(user=Depends(get_current_user)):
        """All 3 books with per-book progress."""
        uid = user["user_id"]
        lang = user["lang"] or "ru"
        result = []
        for book_id, info in BOOKS_INFO.items():
            book_words = get_book_words(book_id)
            total = len(book_words)
            learned = len(await db.get_learned_words_in_book(uid, book_id))
            result.append({
                "book_id": book_id,
                "title": info.get(f"title_{lang}") or info["title_ru"],
                "title_ru": info["title_ru"],
                "author": info["author"],
                "level": info["level"],
                "level_emoji": info["level_emoji"],
                "total_lessons": info["total_lessons"],
                "total_words": total,
                "learned_words": learned,
                "pct": round(learned / total * 100) if total else 0,
                "is_current": user["current_book"] == book_id,
            })
        return result

    @app.get("/api/webapp/volume/{book_id}/lessons")
    async def get_lessons(book_id: int, user=Depends(get_current_user)):
        """Lessons list for a book with per-lesson progress."""
        if book_id not in BOOKS_INFO:
            raise HTTPException(status_code=404, detail="Book not found")
        uid = user["user_id"]
        total = get_total_lessons(book_id)
        learned_all = await db.get_learned_words_in_book(uid, book_id)
        learned_set = set(learned_all)
        lessons = []
        for lesson_num in range(1, total + 1):
            words = get_lesson_words(lesson_num, book_id)
            lesson_word_ids = {w["id"] for w in words}
            learned_count = len(lesson_word_ids & learned_set)
            lessons.append({
                "lesson": lesson_num,
                "total_words": len(words),
                "learned_words": learned_count,
                "pct": round(learned_count / len(words) * 100) if words else 0,
                "is_current": (user["current_book"] == book_id
                               and user["current_lesson"] == lesson_num),
            })
        return lessons

    @app.get("/api/webapp/lesson/{book_id}/{lesson}")
    async def get_lesson_content(book_id: int, lesson: int,
                                 user=Depends(get_current_user)):
        """Word cards for a lesson."""
        lang = user["lang"] or "ru"
        words = get_lesson_words(lesson, book_id)
        if not words:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return {
            "book_id": book_id,
            "lesson": lesson,
            "words": [
                {
                    "id": w["id"],
                    "ar": w["ar"],
                    "trans": w.get("trans", ""),
                    "translation": get_label(w, lang),
                    "ru": w.get("ru", ""),
                    "tj": w.get("tj", ""),
                    "en": w.get("en", ""),
                    "uz": w.get("uz", ""),
                }
                for w in words
            ],
        }

    # ── Quiz ─────────────────────────────────────────────────────────

    @app.post("/api/webapp/quiz/start")
    async def start_quiz(body: QuizStartBody, user=Depends(get_current_user)):
        """Start a quiz session. Returns first question."""
        uid = user["user_id"]
        lang = user["lang"] or "ru"
        words = get_lesson_words(body.lesson, body.book)
        if not words:
            raise HTTPException(status_code=404, detail="Lesson not found")
        shuffled_ids = [w["id"] for w in words]
        random.shuffle(shuffled_ids)
        await db.set_session(
            uid,
            lesson=body.lesson, book=body.book,
            card_index=0, word_index=0, failures=0,
            phase=f"webapp_{body.mode}",
            test_word_ids=json.dumps(shuffled_ids),
        )
        return _make_visual_question(shuffled_ids, 0, body.book, lang, body.mode)

    @app.post("/api/webapp/quiz/answer")
    async def answer_quiz(body: QuizAnswerBody, user=Depends(get_current_user)):
        """Submit answer. Returns {correct, feedback, next_question | done}."""
        uid = user["user_id"]
        lang = user["lang"] or "ru"
        session = await db.get_session(uid)
        if not session:
            raise HTTPException(status_code=400, detail="No active session")

        shuffled_ids = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]
        correct_word = get_word_by_id(body.word_id)

        # Check answer
        if body.mode == "visual":
            is_correct = (body.chosen_id == body.word_id)
        elif body.mode == "written":
            is_correct = check_answer(body.typed or "", correct_word)
        else:  # arabic
            is_correct = check_arabic_answer(body.typed or "", correct_word)

        if is_correct:
            new_idx = idx + 1
            await db.set_session(uid, word_index=new_idx, failures=0)
            if new_idx >= len(shuffled_ids):
                # Lesson done — mark all as learned
                book = session["book"]
                lesson = session["lesson"]
                week = (lesson - 1) // 7 + 1
                words = get_lesson_words(lesson, book)
                for w in words:
                    await db.mark_word(uid, w["id"], "learned", week, book)
                await db.update_user(uid, current_lesson=lesson + 1, state="idle")
                await db.clear_session(uid)
                return {"correct": True, "done": True,
                        "feedback": get_label(correct_word, lang)}
            return {
                "correct": True,
                "done": False,
                "feedback": get_label(correct_word, lang),
                "next": _make_visual_question(
                    shuffled_ids, new_idx, session["book"], lang, body.mode
                ),
            }
        else:
            failures = session["failures"] + 1
            await db.set_session(uid, failures=failures)
            result = {
                "correct": False,
                "failures": failures,
                "feedback": get_label(correct_word, lang),
            }
            if failures >= MAX_FAILURES:
                # Reset: reshuffle
                new_shuffle = list(shuffled_ids)
                random.shuffle(new_shuffle)
                await db.set_session(uid, word_index=0, failures=0,
                                     test_word_ids=json.dumps(new_shuffle))
                result["reset"] = True
                result["next"] = _make_visual_question(
                    new_shuffle, 0, session["book"], lang, body.mode
                )
                # Motivational text
                fresh = await db.get_user(uid)
                fi = fresh["fail_texts_index"] or 0
                from texts import get_fail_text
                result["motivation"] = get_fail_text(lang, fi)
                await db.update_user(uid, fail_texts_index=fi + 1)
            else:
                result["next"] = _make_visual_question(
                    shuffled_ids, idx, session["book"], lang, body.mode
                )
            return result

    def _make_visual_question(shuffled_ids: list, idx: int,
                               book: int, lang: str, mode: str) -> dict:
        """Build question object for frontend."""
        word = get_word_by_id(shuffled_ids[idx])
        if not word:
            return {}
        q: dict = {
            "idx": idx,
            "total": len(shuffled_ids),
            "word_id": word["id"],
            "ar": word["ar"],
            "trans": word.get("trans", ""),
            "mode": mode,
        }
        if mode == "visual":
            book_words = get_book_words(book)
            labels, _, word_ids = make_choices(word, book_words, lang)
            q["choices"] = [
                {"label": labels[i], "word_id": word_ids[i]}
                for i in range(len(labels))
            ]
        elif mode == "written":
            q["prompt"] = get_label(word, lang)  # not used but helpful
        return q

    # ── Umrah Guide ──────────────────────────────────────────────────

    @app.get("/api/webapp/umrah/sections")
    async def get_umrah_sections(user=Depends(get_current_user)):
        """List all guide sections with metadata."""
        lang = user["lang"] or "ru"
        result = []
        for key, sec in SECTIONS.items():
            title_key = f"title_{lang}"
            result.append({
                "key": key,
                "emoji": sec["emoji"],
                "title": sec.get(title_key) or sec["title_ru"],
                "phrase_count": len(sec["phrases"]),
            })
        return result

    @app.get("/api/webapp/umrah/section/{section_key}")
    async def get_umrah_section(section_key: str, user=Depends(get_current_user)):
        """Full section content in user's language."""
        if section_key not in SECTIONS:
            raise HTTPException(status_code=404, detail="Section not found")
        lang = user["lang"] or "ru"
        sec = SECTIONS[section_key]
        lang_map = {"ar": "ru"}  # 'ar' as UI lang → show 'ru' content (fallback)
        content_lang = lang if lang in ("ru", "tj", "en", "uz") else "ru"
        title_key = f"title_{content_lang}"
        return {
            "key": section_key,
            "emoji": sec["emoji"],
            "title": sec.get(title_key) or sec["title_ru"],
            "phrases": [
                {
                    "ar": p["ar"],
                    "trans": p.get("trans", p["ar"]),
                    "translation": p.get(content_lang) or p["ru"],
                }
                for p in sec["phrases"]
            ],
        }

    @app.post("/api/webapp/umrah/quiz/start")
    async def start_umrah_quiz(body: UmrahQuizStartBody,
                               user=Depends(get_current_user)):
        """Start umrah guide test. Returns first visual question."""
        if body.section_key not in SECTIONS:
            raise HTTPException(status_code=404, detail="Section not found")
        uid = user["user_id"]
        lang = user["lang"] or "ru"
        test_refs = get_test_phrases(body.section_key, count=body.count)
        await db.set_session(
            uid, lesson=0, book=0, card_index=0, word_index=0,
            failures=0, phase="webapp_guide_visual",
            test_word_ids=json.dumps(test_refs),
        )
        return _make_guide_question(test_refs, 0, lang, "visual")

    @app.post("/api/webapp/umrah/quiz/answer")
    async def answer_umrah_quiz(body: UmrahQuizAnswerBody,
                                user=Depends(get_current_user)):
        """Submit guide quiz answer."""
        uid = user["user_id"]
        lang = body.lang or user["lang"] or "ru"
        session = await db.get_session(uid)
        if not session:
            raise HTTPException(status_code=400, detail="No active session")

        test_refs = json.loads(session["test_word_ids"] or "[]")
        idx = session["word_index"]

        try:
            c_sec, c_ph = map(int, body.correct_ref.split(":"))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid correct_ref")

        correct_phrase = get_phrase(c_sec, c_ph)

        if body.mode == "visual":
            if not body.chosen_ref:
                raise HTTPException(status_code=400, detail="chosen_ref required")
            ch_sec, ch_ph = map(int, body.chosen_ref.split(":"))
            is_correct = (ch_sec == c_sec and ch_ph == c_ph)
        else:  # written
            content_lang = lang if lang in ("ru", "tj", "en", "uz") else "ru"
            is_correct = check_guide_answer(body.typed or "", correct_phrase, content_lang)

        correct_label = correct_phrase.get(
            lang if lang in ("ru", "tj", "en", "uz") else "ru"
        ) or correct_phrase["ru"]

        if is_correct:
            new_idx = idx + 1
            await db.set_session(uid, word_index=new_idx, failures=0)
            if new_idx >= len(test_refs):
                # Test done
                await db.update_user(uid, state="idle")
                await db.clear_session(uid)
                return {"correct": True, "done": True, "feedback": correct_label}
            return {
                "correct": True,
                "done": False,
                "feedback": correct_label,
                "next": _make_guide_question(test_refs, new_idx, lang, body.mode),
            }
        else:
            failures = session["failures"] + 1
            await db.set_session(uid, failures=failures)
            result = {
                "correct": False,
                "failures": failures,
                "feedback": correct_label,
            }
            if failures >= MAX_FAILURES:
                new_refs = list(test_refs)
                random.shuffle(new_refs)
                await db.set_session(uid, word_index=0, failures=0,
                                     test_word_ids=json.dumps(new_refs))
                result["reset"] = True
                result["next"] = _make_guide_question(new_refs, 0, lang, body.mode)
                fresh = await db.get_user(uid)
                fi = fresh["fail_texts_index"] or 0
                from texts import get_fail_text
                result["motivation"] = get_fail_text(lang, fi)
                await db.update_user(uid, fail_texts_index=fi + 1)
            else:
                result["next"] = _make_guide_question(test_refs, idx, lang, body.mode)
            return result

    def _make_guide_question(test_refs: list, idx: int,
                              lang: str, mode: str) -> dict:
        content_lang = lang if lang in ("ru", "tj", "en", "uz") else "ru"
        sec_idx, ph_idx = test_refs[idx]
        phrase = get_phrase(sec_idx, ph_idx)
        q = {
            "idx": idx,
            "total": len(test_refs),
            "correct_ref": f"{sec_idx}:{ph_idx}",
            "ar": phrase["ar"],
            "trans": phrase.get("trans", phrase["ar"]),
            "mode": mode,
        }
        if mode == "visual":
            choices_raw = make_guide_choices(sec_idx, ph_idx)
            q["choices"] = [
                {
                    "ref": f"{cs}:{cp}",
                    "label": (get_phrase(cs, cp).get(content_lang)
                              or get_phrase(cs, cp)["ru"]),
                }
                for cs, cp in choices_raw
            ]
        return q

    # ── Statistics ───────────────────────────────────────────────────

    @app.get("/api/webapp/stats")
    async def get_stats(user=Depends(get_current_user)):
        """Statistics screen data."""
        stats = await db.get_webapp_stats(user["user_id"])
        return stats

    # ── Ask Teacher ──────────────────────────────────────────────────

    @app.post("/api/webapp/question", status_code=201)
    async def ask_question(body: AskQuestionBody, user=Depends(get_current_user)):
        text = body.question.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        qid = await db.save_question(user["user_id"], text)
        return {"ok": True, "id": qid}

    @app.get("/api/webapp/questions")
    async def get_my_questions(user=Depends(get_current_user)):
        """All questions + answers for the current user."""
        rows = await db.get_questions_for_user(user["user_id"])
        return [
            {
                "id": r["id"],
                "question": r["text"],
                "answer": r["answer"],
                "answered": r["answered"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ]

    # ── Teacher endpoints ────────────────────────────────────────────

    @app.get("/api/webapp/teacher/stats")
    async def teacher_stats(user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        students = await db.get_students_sorted()
        total_words = sum(int(s.get("learned", 0)) for s in students)
        active = sum(1 for s in students if s.get("learned", 0) > 0)
        unanswered = await db.get_unanswered_questions()
        return {
            "total_students": len(students),
            "active_students": active,
            "total_words_learned": total_words,
            "unanswered_questions": len(unanswered),
            "students": [
                {
                    "user_id": s["user_id"],
                    "name": s["name"] or "—",
                    "current_book": s["current_book"],
                    "current_lesson": s["current_lesson"],
                    "learned": int(s.get("learned", 0)),
                    "total_app_time": int(s.get("total_app_time") or 0),
                }
                for s in students[:20]
            ],
        }

    @app.get("/api/webapp/teacher/questions")
    async def teacher_get_questions(user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        rows = await db.get_unanswered_questions()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "user_name": r["name"] or "—",
                "question": r["text"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ]

    @app.post("/api/webapp/teacher/answer/{question_id}")
    async def teacher_answer(question_id: int, body: AnswerBody,
                             user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        await db.answer_question(question_id, body.answer.strip())
        q = await db.get_question_by_id(question_id)
        if q:
            try:
                import httpx as _httpx
                async with _httpx.AsyncClient(timeout=5) as client:
                    await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": q["user_id"],
                            "text": (
                                f"✅ Учитель "
                                f"ответил на "
                                f"ваш вопрос:"
                                f"\n\n❓ {q['text']}\n\n\U0001f4ac {body.answer.strip()}"
                            ),
                        },
                    )
            except Exception:
                pass
        return {"ok": True}

    @app.post("/api/webapp/teacher/question/{question_id}/delete")
    async def teacher_delete_question(question_id: int, user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        await db.delete_question(question_id)
        return {"ok": True}

    @app.post("/api/webapp/teacher/question/{question_id}/dismiss")
    async def teacher_dismiss_question(question_id: int, user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        await db.delete_question(question_id)
        return {"ok": True}

    @app.post("/api/webapp/teacher/broadcast")
    async def teacher_broadcast(body: BroadcastBody, user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        students = await db.get_all_users()
        sent, failed = 0, 0
        try:
            import httpx as _httpx
            async with _httpx.AsyncClient(timeout=5) as client:
                for s in students:
                    if s["user_id"] == TEACHER_ID:
                        continue
                    try:
                        await client.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": s["user_id"],
                                "text": f"\U0001f4e2 Сообщение от учителя:\n\n{body.message}",
                            },
                        )
                        sent += 1
                    except Exception:
                        failed += 1
        except Exception:
            pass
        return {"ok": True, "sent": sent, "failed": failed}

    @app.post("/api/webapp/teacher/message")
    async def teacher_personal_message(body: PersonalMessageBody,
                                       user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        try:
            import httpx as _httpx
            async with _httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": body.user_id,
                        "text": f"✉️ Личное сообщение от учителя:\n\n{body.message}",
                    },
                )
        except Exception:
            pass
        return {"ok": True}

    # ── App config (global background etc.) ─────────────────────────

    @app.get("/api/webapp/config")
    async def get_app_config(user=Depends(get_current_user)):
        """Returns global app config (background URL set by teacher)."""
        if not db._pool:
            return {"bg_url": ""}
        try:
            await db._pool.execute(
                "CREATE TABLE IF NOT EXISTS app_config (key TEXT PRIMARY KEY, value TEXT);"
            )
            row = await db._pool.fetchrow(
                "SELECT value FROM app_config WHERE key='global_bg'"
            )
            return {"bg_url": (row["value"] or "") if row else ""}
        except Exception:
            return {"bg_url": ""}

    @app.post("/api/webapp/teacher/config/bg")
    async def set_global_bg(body: BgConfigBody, user=Depends(get_current_user)):
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        await db._pool.execute(
            "CREATE TABLE IF NOT EXISTS app_config (key TEXT PRIMARY KEY, value TEXT);"
        )
        await db._pool.execute(
            """
            INSERT INTO app_config (key, value) VALUES ('global_bg', $1)
            ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value
            """,
            body.bg_url,
        )
        return {"ok": True}

    # ── Extended teacher endpoints ───────────────────────────────────

    @app.get("/api/webapp/teacher/students/all")
    async def teacher_all_students(user=Depends(get_current_user)):
        """All students sorted by progress (no 20-limit)."""
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        students = await db.get_students_sorted()
        return [
            {
                "user_id": s["user_id"],
                "name": s["name"] or "—",
                "current_book": s["current_book"],
                "current_lesson": s["current_lesson"],
                "learned": int(s.get("learned", 0)),
                "total_app_time": int(s.get("total_app_time") or 0),
            }
            for s in students
        ]

    @app.get("/api/webapp/teacher/lazy")
    async def teacher_lazy(user=Depends(get_current_user)):
        """Students who have not learned a single word yet."""
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        rows = await db.get_lazy_students()
        return [
            {"user_id": r["user_id"], "name": r["name"] or "—", "lang": r.get("lang") or "ru"}
            for r in rows
        ]

    @app.get("/api/webapp/teacher/questions/all")
    async def teacher_all_questions(user=Depends(get_current_user)):
        """All questions including answered — for teacher history view."""
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        rows = await db.get_all_questions()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "user_name": r["name"] or "—",
                "question": r["text"],
                "answer": r.get("answer"),
                "answered": bool(r.get("answered", False)),
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ]

    class StudentResetBody(BaseModel):
        user_id: int

    @app.post("/api/webapp/teacher/student/reset")
    async def teacher_student_reset(body: StudentResetBody, user=Depends(get_current_user)):
        """Reset a student's progress (teacher action)."""
        if user["user_id"] != TEACHER_ID:
            raise HTTPException(status_code=403, detail="Teacher only")
        await db.reset_all_progress(body.user_id)
        return {"ok": True}

    return app
