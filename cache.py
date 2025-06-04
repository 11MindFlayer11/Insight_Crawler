import redis
import json
import logging

logger = logging.getLogger(__name__)


class CacheConnectionError(Exception):
    """Custom exception for cache connection issues"""


try:
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    redis_client.ping()

except redis.RedisError as e:
    logger.error(f"Redis connection error: {str(e)}")
    raise CacheConnectionError("Could not connect to Redis") from e


def get_cache(key: str):
    """Retrieve cached data from Redis."""
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except CacheConnectionError as e:
        logger.warning("Using fallback cache")
        return None  # Add in-memory cache fallback here


def set_cache(key: str, data, ttl: int = 3600):
    """Set cache in Redis with optional TTL (seconds)."""
    try:
        redis_client.setex(key, ttl, json.dumps(data))
    except CacheConnectionError as e:
        logger.warning("Cache write failed, proceeding without caching")
