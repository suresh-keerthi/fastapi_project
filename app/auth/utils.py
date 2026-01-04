import logging
from passlib.context import CryptContext
from fastapi.concurrency import run_in_threadpool
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
import jwt
from app.config import config
from app.db.redis import get_redis

# i don't think using therdpool makes any difference because hasing is cpu bound
# i think it is same as direclty hashing 


pwd_context = CryptContext(
        schemes= ["bcrypt"],
        deprecated = "auto"
)

async def hash_password(password:str):
    # bcrypt only accepts passwords up to 72 bytes; validate to provide a clear error
    if len(password.encode("utf-8")) > 72:
        raise ValueError("password too long for bcrypt (max 72 bytes)")
    return  await run_in_threadpool(
        pwd_context.hash,
        password
    )


async def verify_password(password:str, hashed_password:str):
    return await run_in_threadpool(
           pwd_context.verify,
           password,
           hashed_password 
    )
    

def create_tokens(user_data : dict, expiry:timedelta = timedelta(minutes=30), refresh: bool = False):
    payload = {
        "user": user_data,
        "exp" : int((datetime.now(timezone.utc) + expiry).timestamp()),
        "jti" :  str(uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        payload= payload,
        key= config.JWT_SECRET_KEY,
        algorithm= "HS256"
    )

    return token

def decode_token(token:str):
    try:
        payload = jwt.decode(
            jwt= token,
            key= config.JWT_SECRET_KEY,
            algorithms= ["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        logging.warning("JWT decode failed: expired token (%s)", e)
        return None
    except jwt.InvalidTokenError as e:
        logging.warning("JWT decode failed: invalid token (%s)", e)
        return None
    except Exception as e:
        logging.exception("Unexpected error decoding JWT: %s", e)
        return None

async def black_list_jti(jti:str, expiry: int):
    ttl =  expiry - int(datetime.now(timezone.utc).timestamp())

    if ttl <=0:
        return 
    redis = get_redis()
    await redis.set(
        name=jti,
        value="revoked",
        ex= ttl

    )

async def is_revoked(jti:str) -> bool:
    redis = get_redis()
    return ((await redis.exists(jti)) == 1 )