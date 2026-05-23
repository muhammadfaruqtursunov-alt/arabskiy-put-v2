import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
TEACHER_ID = int(os.environ.get("TEACHER_ID", "0"))
WORDS_PER_LESSON = 10
WEEKLY_TEST_COUNT = 25
MAX_FAILURES = 3
