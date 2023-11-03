"""
FastAPI route to simulate a Redis cache
the cache is a REDIS server started with the connection parameters as above
this app can be started from the project rootwith:
    * poetry run uvicorn uvicorn app.fastapi_cache:app --reload
this will place uvicorn listening on port 8000
redis can be started on the Mac in background with
    * brew services start redis  
to check the status:
    * brew services info redis  
if redis is not up where expected the FastAPI will return a 500 error
the redis cache seems to be persisting through start/stop (file dump.rdb in root of project)
"""
import logging

import redis
from fastapi import FastAPI
from starlette.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Redis connection
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""  # Add your password here if required

# Connect to Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
)

app = FastAPI()


@app.get("/cache/{item}")
async def cache_item(item: str):
    """our FastAPI async cache function
    it will be called with GET and a string as its path argument
    if the string is not found in the cache it will return a 202 and insert the string in the cace
    if the string is found it will return a 200
    """
    # Check if the item is in the cache
    if redis_client.exists(item):
        # Item is in cache, return 200 OK
        logger.info("Cache hit for item: %s", item)
        return JSONResponse(status_code=200, content={"status": "hit", "item": item})
    else:
        # Item not in cache, queue for insertion
        # Set the item with a placeholder value indicating it's being processed.
        # You can also use a TTL for the cache entry if necessary.
        redis_client.set(
            item, "value_being_processed", ex=300
        )  # ex is the expiration time in seconds.

        # Return 202 Accepted to indicate the item is not in the cache
        # but will be added.
        logger.info("Cache miss for item: %s. Item will be inserted.", item)
        return JSONResponse(status_code=202, content={"status": "miss", "item": item})
