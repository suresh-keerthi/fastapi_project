from redis.asyncio import Redis
from app.config import config

_redis: Redis | None = None

async def init_redis():
    global _redis
    _redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=0,
        decode_responses=True,
    )

async def close_redis():
    if _redis:
        await _redis.close()

def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis

