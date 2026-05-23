# -*- coding: utf-8 -*-
"""
Standalone FastAPI entry-point — runs as the Railway 'web' process.
Has its own asyncpg pool, completely independent from bot.py.

Start: uvicorn api_server:app --host 0.0.0.0 --port $PORT
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

import database as db
from webapp_api import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")


async def _connect_db_background() -> None:
    """Connect to the DB in background so startup never blocks."""
    for attempt in range(5):
        try:
            logger.info(f"DB connect attempt {attempt + 1}/5 ...")
            pool = await asyncio.wait_for(db.get_pool(), timeout=15)
            db._pool = pool
            logger.info("✓ DB pool ready")
            return
        except Exception as exc:
            logger.error(f"DB attempt {attempt + 1} failed: {exc}")
            await asyncio.sleep(3)
    logger.error("✗ All DB attempts failed — API endpoints will return 503")


@asynccontextmanager
async def _lifespan(application: FastAPI):
    # ── Startup: fire DB init in background, don't block uvicorn ──
    asyncio.create_task(_connect_db_background())
    logger.info("API server started — DB connecting in background")
    yield
    # ── Shutdown ──────────────────────────────────────────────────
    if db._pool:
        await db._pool.close()
        logger.info("DB pool closed.")


# Build app with lifespan injected via constructor
app = create_app(lifespan=_lifespan)
