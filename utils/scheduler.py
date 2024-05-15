from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from os import environ
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

job_store = (
    MemoryJobStore()
)  # FIXME due to a bug in the apscheduler + gunicorn combination


message_scheduler: BaseScheduler = AsyncIOScheduler(
    timezone='Europe/Moscow',
    jobstores={
        "default": job_store,
    },
    executors={"default": AsyncIOExecutor(), "cron": ThreadPoolExecutor()},
    # timezone=utc,
    job_defaults={
        "coalesce": True,  # Trigger only one job to make up for missed jobs.
        "max_instances": 1,  # Allow only one execution of a job per time.
    },
)
