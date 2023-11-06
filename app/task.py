# pylint: disable=line-too-long
""" file task.py 
    to launch the Celery task
    celery --app=app.task.app worker --concurrency=1 --loglevel=DEBUG
    from the project root in the right poetry env

    to have this relaunched every time it changes add watchdog to poetry dev group
    and then
    watchmedo auto-restart --directory=./app --pattern=task.py -- celery --app=app.task.app worker --concurrency=1 --loglevel=DEBUG
"""
from time import sleep
import os
from celery.app import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)


@app.task
def dummy_task(name="Bob") -> str:
    """simple"""
    sleep(10)
    return f"Hello {name}!"
