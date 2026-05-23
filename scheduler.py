import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import database as db
from texts import get_reminder_text

scheduler = AsyncIOScheduler(timezone=pytz.utc)
_bot = None


def setup(bot):
    global _bot
    _bot = bot
    scheduler.add_job(
        send_reminders,
        CronTrigger(minute="*", timezone=pytz.utc),
        id="reminders",
    )
    scheduler.start()
    logging.info("Scheduler started.")


async def send_reminders():
    try:
        users = await db.get_all_users()
        for user in users:
            if not user["reminder_time"]:
                continue
            try:
                tz = pytz.timezone(user["timezone"])
                now = datetime.now(tz)
                current_time = f"{now.hour:02d}:{now.minute:02d}"
                if user["reminder_time"] == current_time:
                    lang = user["lang"] if user["lang"] in ("ru", "tj") else "ru"
                    weekday = now.weekday()
                    text = get_reminder_text(lang, weekday)
                    await _bot.send_message(user["user_id"], f"{text}\n\n/lesson")
            except Exception as e:
                logging.warning(f"Reminder error for {user['user_id']}: {e}")
    except Exception as e:
        logging.error(f"Scheduler error: {e}")
