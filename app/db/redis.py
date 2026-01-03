from redis.asyncio import Redis
from app.config import config

redis = Redis(
    host= config.REDIS_HOST,
    port= config.REDIS_PORT,
    db = 0,
    decode_responses= True
)


