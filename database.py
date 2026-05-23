import asyncpg
from datetime import date, timedelta
from config import DATABASE_URL, TEACHER_ID

_pool = None


async def get_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=30,   # fail fast instead of hanging forever
    )


async def init_db(pool):
    global _pool
    _pool = pool
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            name TEXT,
            lang TEXT DEFAULT 'ru',
            current_lesson INTEGER DEFAULT 1,
            current_book INTEGER DEFAULT 1,
            state TEXT DEFAULT 'idle',
            reminder_time TEXT DEFAULT NULL,
            timezone TEXT DEFAULT 'Asia/Dushanbe',
            fail_texts_index INTEGER DEFAULT 0,
            last_rank INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS sessions (
            user_id BIGINT PRIMARY KEY,
            lesson INTEGER DEFAULT 1,
            book INTEGER DEFAULT 1,
            card_index INTEGER DEFAULT 0,
            word_index INTEGER DEFAULT 0,
            failures INTEGER DEFAULT 0,
            phase TEXT DEFAULT 'cards',
            test_word_ids TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS progress (
            user_id BIGINT,
            word_id INTEGER,
            status TEXT DEFAULT 'new',
            week INTEGER DEFAULT 1,
            book INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, word_id)
        );
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            text TEXT,
            answer TEXT DEFAULT NULL,
            answered BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS app_config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    # Migrations for existing DBs
    await pool.execute("""
        ALTER TABLE users        ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'Asia/Dushanbe';
        ALTER TABLE users        ADD COLUMN IF NOT EXISTS current_book INTEGER DEFAULT 1;
        ALTER TABLE users        ADD COLUMN IF NOT EXISTS last_rank INTEGER DEFAULT NULL;
        ALTER TABLE sessions     ADD COLUMN IF NOT EXISTS book INTEGER DEFAULT 1;
        ALTER TABLE progress     ADD COLUMN IF NOT EXISTS book INTEGER DEFAULT 1;
    """)
    # Mini App: streak tracking
    await pool.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS streak INTEGER DEFAULT 0;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity TEXT DEFAULT NULL;
    """)
    # Mini App: total time in app (seconds)
    await pool.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS total_app_time INTEGER DEFAULT 0;
    """)
    # Migrate old users who had global lesson numbering (1-21 across all books)
    # to per-book numbering: 8→Book 2 Lesson 1, 15→Book 3 Lesson 1, etc.
    await pool.execute("""
        UPDATE users SET current_book=2, current_lesson=current_lesson-7
            WHERE current_book=1 AND current_lesson BETWEEN 8 AND 14;
        UPDATE users SET current_book=3, current_lesson=current_lesson-14
            WHERE current_book=1 AND current_lesson BETWEEN 15 AND 21;
    """)


async def get_user(user_id: int):
    return await _pool.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)


async def create_user(user_id: int):
    await _pool.execute(
        "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
        user_id,
    )


async def update_user(user_id: int, **kwargs):
    fields = ", ".join(f"{k}=${i+2}" for i, k in enumerate(kwargs))
    values = list(kwargs.values())
    await _pool.execute(
        f"UPDATE users SET {fields} WHERE user_id=$1",
        user_id, *values,
    )


async def get_all_users():
    return await _pool.fetch("SELECT * FROM users")


async def get_students_sorted():
    """All students (excluding teacher) sorted by learned-words DESC, then current_book DESC, then current_lesson DESC."""
    return await _pool.fetch("""
        SELECT u.*,
               COALESCE((SELECT COUNT(*) FROM progress p
                         WHERE p.user_id=u.user_id AND p.status='learned'), 0) AS learned
        FROM users u
        WHERE u.user_id <> $1
        ORDER BY learned DESC, u.current_book DESC, u.current_lesson DESC, u.user_id ASC
    """, TEACHER_ID)


async def get_lazy_students():
    """Students who haven't learned a single word yet."""
    return await _pool.fetch("""
        SELECT u.*
        FROM users u
        WHERE u.user_id <> $1
          AND NOT EXISTS (SELECT 1 FROM progress p
                          WHERE p.user_id=u.user_id AND p.status='learned')
        ORDER BY u.created_at DESC
    """, TEACHER_ID)


async def get_session(user_id: int):
    return await _pool.fetchrow("SELECT * FROM sessions WHERE user_id=$1", user_id)


async def set_session(user_id: int, **kwargs):
    existing = await get_session(user_id)
    if existing:
        fields = ", ".join(f"{k}=${i+2}" for i, k in enumerate(kwargs))
        values = list(kwargs.values())
        await _pool.execute(
            f"UPDATE sessions SET {fields} WHERE user_id=$1",
            user_id, *values,
        )
    else:
        kwargs["user_id"] = user_id
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(f"${i+1}" for i in range(len(kwargs)))
        await _pool.execute(
            f"INSERT INTO sessions ({cols}) VALUES ({placeholders})",
            *kwargs.values(),
        )


async def clear_session(user_id: int):
    await _pool.execute("DELETE FROM sessions WHERE user_id=$1", user_id)


async def mark_word(user_id: int, word_id: int, status: str, week: int, book: int = 1):
    await _pool.execute("""
        INSERT INTO progress (user_id, word_id, status, week, book)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id, word_id) DO UPDATE SET status=$3, book=$5
    """, user_id, word_id, status, week, book)


async def get_learned_words(user_id: int, week: int, book: int = None) -> list:
    if book is None:
        rows = await _pool.fetch(
            "SELECT word_id FROM progress WHERE user_id=$1 AND week=$2 AND status='learned'",
            user_id, week,
        )
    else:
        rows = await _pool.fetch(
            "SELECT word_id FROM progress WHERE user_id=$1 AND week=$2 AND book=$3 AND status='learned'",
            user_id, week, book,
        )
    return [r["word_id"] for r in rows]


async def get_learned_words_in_book(user_id: int, book: int) -> list:
    rows = await _pool.fetch(
        "SELECT word_id FROM progress WHERE user_id=$1 AND book=$2 AND status='learned'",
        user_id, book,
    )
    return [r["word_id"] for r in rows]


async def reset_week_progress(user_id: int, week: int, book: int = None):
    if book is None:
        await _pool.execute(
            "UPDATE progress SET status='new' WHERE user_id=$1 AND week=$2",
            user_id, week,
        )
    else:
        await _pool.execute(
            "UPDATE progress SET status='new' WHERE user_id=$1 AND week=$2 AND book=$3",
            user_id, week, book,
        )


async def reset_all_progress(user_id: int):
    """Admin action — wipe a student's progress."""
    await _pool.execute("DELETE FROM progress WHERE user_id=$1", user_id)
    await _pool.execute("DELETE FROM sessions WHERE user_id=$1", user_id)
    await _pool.execute(
        "UPDATE users SET current_lesson=1, current_book=1, state='idle' WHERE user_id=$1",
        user_id,
    )


async def get_total_learned_words(user_id: int) -> int:
    val = await _pool.fetchval(
        "SELECT COUNT(*)::INTEGER FROM progress WHERE user_id=$1 AND status='learned'",
        user_id,
    )
    return int(val or 0)


async def get_user_rank(user_id: int):
    """(rank, total_students) — sorted by total learned desc, then current_book desc, then current_lesson desc."""
    rows = await _pool.fetch("""
        SELECT u.user_id,
               COALESCE((SELECT COUNT(*) FROM progress p
                         WHERE p.user_id=u.user_id AND p.status='learned'), 0) AS learned
        FROM users u
        WHERE u.user_id <> $1
        ORDER BY learned DESC, u.current_book DESC, u.current_lesson DESC, u.user_id ASC
    """, TEACHER_ID)
    total = len(rows)
    rank = next((i + 1 for i, r in enumerate(rows) if r["user_id"] == user_id), None)
    return rank, total


async def save_question(user_id: int, text: str) -> int:
    row = await _pool.fetchrow(
        "INSERT INTO questions (user_id, text) VALUES ($1, $2) RETURNING id",
        user_id, text,
    )
    return row["id"]


async def get_unanswered_questions():
    return await _pool.fetch(
        "SELECT q.*, u.name FROM questions q JOIN users u ON q.user_id=u.user_id "
        "WHERE q.answered=FALSE ORDER BY q.created_at",
    )


async def answer_question(question_id: int, answer: str):
    await _pool.execute(
        "UPDATE questions SET answer=$2, answered=TRUE WHERE id=$1",
        question_id, answer,
    )


async def get_question_by_id(question_id: int):
    return await _pool.fetchrow("SELECT * FROM questions WHERE id=$1", question_id)


async def delete_question(question_id: int):
    await _pool.execute("DELETE FROM questions WHERE id=$1", question_id)


async def update_streak(user_id: int):
    """Update daily streak. Call once per day on login/activity. Safe to call multiple times."""
    today = date.today().isoformat()
    user = await get_user(user_id)
    if not user:
        return
    last = user.get("last_activity")
    if last == today:
        return  # already updated today
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    new_streak = (user["streak"] or 0) + 1 if last == yesterday else 1
    await update_user(user_id, streak=new_streak, last_activity=today)


async def get_questions_for_user(user_id: int):
    """Get all questions submitted by a student (for Mini App)."""
    return await _pool.fetch(
        "SELECT * FROM questions WHERE user_id=$1 ORDER BY created_at DESC",
        user_id,
    )


async def get_all_questions():
    """All questions (including answered) for teacher question history."""
    return await _pool.fetch("""
        SELECT q.*, u.name FROM questions q
        JOIN users u ON q.user_id=u.user_id
        ORDER BY q.created_at DESC LIMIT 200
    """)


async def get_webapp_stats(user_id: int) -> dict:
    """Aggregate stats for Mini App statistics screen."""
    total_learned = await get_total_learned_words(user_id)
    user = await get_user(user_id)
    book_stats = []
    for book_id in (1, 2, 3):
        from words import get_book_words, get_total_lessons
        total_in_book = len(get_book_words(book_id))
        learned_in_book = len(await get_learned_words_in_book(user_id, book_id))
        book_stats.append({
            "book_id": book_id,
            "total": total_in_book,
            "learned": learned_in_book,
            "pct": round(learned_in_book / total_in_book * 100) if total_in_book else 0,
        })
    questions_count = await _pool.fetchval(
        "SELECT COUNT(*) FROM questions WHERE user_id=$1", user_id
    )
    return {
        "total_learned": total_learned,
        "streak": user["streak"] or 0,
        "books": book_stats,
        "questions_asked": int(questions_count or 0),
        "total_app_time": int(user.get("total_app_time") or 0),
    }


async def add_session_time(user_id: int, seconds: int):
    """Accumulate app session time for a user (capped at 24h per call)."""
    secs = max(1, min(int(seconds), 86400))
    await _pool.execute(
        "UPDATE users SET total_app_time = COALESCE(total_app_time, 0) + $2 WHERE user_id=$1",
        user_id, secs,
    )
