"""
FastAPI route to simulate a Redis cache
*** this version uses Celery to actually insert a new cache entry into Redis
the cache is a REDIS server started with the connection parameters as above
this app can be started from the project rootwith:
    * poetry run uvicorn app.fastapi3_cache:app --reload
this will place uvicorn listening on port 8000
redis can be started on the Mac in background with
    * brew services start redis  
to check the status:
    * brew services info redis  
if redis is not up where expected the FastAPI will return a 500 error
the redis cache is persisting through brew start/stop (file dump.rdb in root of project)
but the cache entries have a 3000 seconds expiry
The cache has a string as a key and a dictionary/hash for the URL, author and date keys
These are generated by the faker library
"""
import logging

import redis
from faker import Faker
from fastapi import FastAPI
from starlette.responses import JSONResponse

from app.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

from .celery_worker import insert_into_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_URL = "https://ilmanifesto.it/"

# Connect to Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
)

app = FastAPI()

# Initialize a Faker generator
fake = Faker()


@app.get("/cache/{item}")
async def cache_item(item: str):
    """Endpoint to store and retrieve items from a Redis hash."""
    hash_key = item  # The 'item' is used as the key for the Redis hash

    # Check if the item is in the cache
    if redis_client.exists(hash_key):
        # Item is in cache, return 200 OK and the hash
        logger.info("Cache hit for item: %s", hash_key)
        hash_data = redis_client.hgetall(hash_key)
        return JSONResponse(
            status_code=200, content={"status": "hit", "data": hash_data}
        )
    # Instead of inserting directly into Redis, we send a task to Celery
    else:
        # Generate the fake data
        fakeurl = BASE_URL + fake.slug()
        hash_data = {
            "URL": fakeurl,
            "pubdate": fake.date(),
            "author": fake.name(),
        }

        # Send a task to Celery to insert this into the cache
        insert_into_cache.delay(hash_key, hash_data)

        # Return a response immediately
        logger.info("Cache miss for item: %s. Task sent to Celery.", hash_key)
        return JSONResponse(
            status_code=202, content={"status": "queued", "item": hash_key}
        )


# Example of the hash set operation
@app.post("/cache/{item}")
async def create_cache_item(item: str, url: str, pubdate: str, author: str):
    """Endpoint to create a new item in the Redis hash."""
    hash_data = {"URL": url, "pubdate": pubdate, "author": author}
    redis_client.hset(item, mapping=hash_data)
    redis_client.expire(item, 300)  # Optional: set TTL for the key.
    return {"status": "created", "data": hash_data}
