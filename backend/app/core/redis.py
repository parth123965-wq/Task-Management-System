from redis.asyncio import ConnectionPool, Redis
from app.core.config import setting

redis_pool: ConnectionPool|None = None

async def init_redis_pool()->None:
    global redis_pool
    redis_pool = ConnectionPool.from_url(
        setting.REDIS_URL,
        max_connections=20,
        decode_responses=True
    )
    
async def redis_close():
    global redis_pool
    if redis_pool:
        return redis_pool.disconnect()
    
async def get_redis()->Redis:
    return Redis(connection_pool=redis_pool)