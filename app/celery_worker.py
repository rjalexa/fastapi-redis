""" Celery task to insert an entry in the Redis cache
from the project root folder: 
    poetry run celery -A app.celery_worker worker --loglevel=DEBUG
Also installed Flower to monitor the Celery queues etc
after the Celery queue is running then use:
    poetry run celery --broker=redis://localhost:6379/0 flower
to add flower monitoring
"""
from celery import Celery
import redis
from app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


# Initialize Celery
celery_app = Celery(
    "worker", backend="redis://localhost:6379/0", broker="redis://localhost:6379/0"
)


# Define a Celery task
@celery_app.task
def insert_into_cache(hash_key, hash_data):
    """our Celery task"""
    redis_client = redis.StrictRedis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
    )
    redis_client.hset(hash_key, mapping=hash_data)
    redis_client.expire(hash_key, 3000)  # Set TTL for the key.
