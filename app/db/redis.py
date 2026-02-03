from redis.asyncio import Redis
from app.config import config

_redis: Redis | None = None #this is a singleton instance which will be used throughout the app(it is client connection to redis server) 
                            #why singleton? because we dont want to create multiple connections to redis server
                            # because it is expensive operation
                            #then what if multiple requests come at the same time can they use same instance?
                            # yes because redis client is thread safe and can handle multiple requests at the same time
                            #thred safe means multiple threads can access the same instance without any issues

async def init_redis():
    global _redis
    _redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=0, #db index
        decode_responses=True,
    )

async def close_redis():
    if _redis:
        await _redis.close()

def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis

