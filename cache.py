import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


def get_cache(key: str):
    """Retrieve cached data from Redis."""
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None


def set_cache(key: str, data, ttl: int = 3600):
    """Set cache in Redis with optional TTL (seconds)."""
    redis_client.setex(key, ttl, json.dumps(data))
