# A FastAPI/Redis/Celery/Locust/Flower demo project

This is a demo project to show how a FastAPI app can
rapidly lookup a key and related data from a Redis cache
but if the key is unknown the FastAPI app will delegate its
processing to a Celery queue which in turn will trigger a
(simlated with Faker ) long running computing process to compute the
related data and store the key and related data in the Redis cache.

There's also a little Locust project to simulate a load on this
FastAPI program and its backend

This is the project tree:

```
.
├── README.md
├── app
│   ├── __init__.py
│   ├── celery_worker.py
│   ├── config.py
│   ├── fastapi_redis_celery.py
├── dump.rdb
├── poetry.lock
├── pyproject.toml
├── redis_start.sh
└── tests
└── performance_tests
└── locust_test.py
```

Instructions to run:

This project has been developed on a Mac in Nov-2023 using Poetry to
prepare a virtual environments with python and its needed libraries.

So after a poetry install you should be ready to go:

1. Launch Redis - Mac -> brew services start redis
   then cd to the project root su such as ~/code/fastapi-redis and
2. launch the uvicorn FastAPI endpoint
   poetry run uvicorn app.fastapi_redis_celery:app --reload
3. launch Celery
   poetry run celery -A app.celery_worker worker --loglevel=DEBUG
4. run Locust to launch a load test
   poetry run locust -f tests/performance_tests/locust_test.py
   go with the browser to http://127.0.0.1:8089/
   Set the max number of concurrent users, how many to add each second
   and the FastAPI uvicorn application URL: http://127.0.0.1:8000
5. It is possible to monitor Celery with Flower:
   poetry run celery --broker=redis://localhost:6379/0 flower
   Then, you can visit flower in your web browser :
   http://localhost:5555
