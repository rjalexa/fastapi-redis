"""  another small FastAPI demo leveraging Celery tasks
     to run it, from the project root:
        poetry run uvicorn app.producer:app
"""
from fastapi import FastAPI
from pydantic import BaseModel
from celery.result import AsyncResult

# the following imports the Celery task(s) defined in task.py
# in this minimal example it's only dummy_task()
from . import task

app = FastAPI()


class TaskOut(BaseModel):
    """Pydantic model for a task id and status"""

    id: str
    status: str


def _to_task_out(r: AsyncResult) -> TaskOut:
    """utility function meant to convert an AsyncResult object into a TaskOut object"""
    return TaskOut(id=r.task_id, status=r.status)


@app.get("/start")
def start() -> TaskOut:
    """In Postman add the following to the Tests tab of the GET of this
        var responseJson = pm.response.json();
        pm.environment.set("task_id", responseJson.id);
    this will set an env var called task_id with the value returned by the GET"""
    r = task.dummy_task.delay()
    return _to_task_out(r)


@app.get("/status")
def status(task_id: str) -> TaskOut:
    """in Postman use it with a GET as follows
    http://127.0.0.1:8000/status/?task_id={{task_id}}
    where task_id is an env var set by the start endpoint
    """
    r = task.app.AsyncResult(task_id)
    return _to_task_out(r)
