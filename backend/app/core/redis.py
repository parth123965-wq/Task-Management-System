from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
import redis
from app.core.config import setting

redis_pool: ConnectionPool|None = None

retry_handler = Retry(ExponentialBackoff(), retries=3)

async def init_redis_pool()->None:
    global redis_pool
    redis_pool = ConnectionPool.from_url(
        setting.REDIS_URL,
        max_connections=20,
        decode_responses=True,
        encoding="utf-8",
        retry=retry_handler,
        retry_on_error=[redis.ConnectionError, redis.TimeoutError],
    )
    
async def redis_close():
    global redis_pool
    if redis_pool:
        return redis_pool.disconnect()
    
async def get_redis()->Redis:
    return Redis(connection_pool=redis_pool)