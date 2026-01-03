from redis.asyncio import Redis
import asyncio
redis = Redis(
    host= "localhost",
    port= 6379,
    db=0, # where db means database index and 0 means the first database
    decode_responses= True # where decode_responses=True means that the responses will be decoded to strings
)

async def set():
    await redis.set(name="key", value="value", ex=60*60)
    
asyncio.run(set())