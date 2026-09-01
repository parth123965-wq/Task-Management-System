from redis.asyncio import Redis
from secrets import randbelow
from app.core.config import setting
from fastapi import HTTPException, status
import secrets
import json

class OtpService:
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def otp_key(self, purpose: str, identifier: str)-> str:
        return f"otp:{purpose}:{identifier}"

    async def otp_attempt(self, purpose: str, identifier: str)-> str:
        return f"otp_attempts:{purpose}:{identifier}"
    
    async def otp_cooldown(self, purpose: str, identifier: str)-> str:
            return f"otp_cooldown:{purpose}:{identifier}"
        
    async def otp_data_key(self, purpose: str, identifier: str)-> str:
        return f"otp_data:{purpose}:{identifier}"
    
    async def otp_generate(self):
        return (randbelow(900000) + 100000)
    
    async def save_otp(self, key: str, attempt: str, cooldown: str, otp_value: int, otp_data_key: str, otp_data:dict) -> None:
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(key,otp_value,ex=setting.OTP_EXPIRY)
            pipe.set(attempt,0,ex=setting.OTP_EXPIRY)
            pipe.set(cooldown,"1",ex=setting.OTP_EXPIRY)
            pipe.set(otp_data_key,json.dumps(otp_data),ex=setting.OTP_EXPIRY)
            await pipe.execute()
            
    async def otp_generate_save(self, purpose: str, identifier: str, data: dict):
        otp_value = await self.otp_generate()
        key = await self.otp_key(purpose,identifier)
        attempt = await self.otp_attempt(purpose,identifier)
        cooldown = await self.otp_cooldown(purpose,identifier)
        otp_data_key = await self.otp_data_key(purpose,identifier)
        if await self.redis.exists(cooldown):
            ttl = await self.redis.ttl(cooldown)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {ttl} seconds before requesting a new OTP."
            )
        await self.save_otp(key=key,attempt=attempt,cooldown=cooldown,otp_value=otp_value,otp_data_key=otp_data_key,otp_data=data)
        return otp_value
    
    async def verify_otp(self, purpose: str, identifier: str, otp_value: int)->dict:
        otp_keys = await self.otp_key(purpose,identifier)
        attempt_key = await self.otp_attempt(purpose,identifier)
        attempt = await self.redis.incr(attempt_key)
        cooldown_key = await self.otp_cooldown(purpose,identifier)
        stored_otp = await self.redis.get(otp_keys)
        if attempt > setting.OTP_ATTEMPTS:
            await self.redis.delete(otp_keys,attempt_key,cooldown_key)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invalid attempts. This OTP has been invalidated."
            )
        if not secrets.compare_digest(stored_otp, otp_value):
            remaining = setting.OTP_MAX_ATTEMPTS - attempt
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid OTP. {remaining} attempt(s) remaining."
            )
        otp_data_key = await self.otp_data_key(purpose,identifier)
        cached = await self.redis.get(otp_data_key)
        if not cached:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Data not Found Please try Again."
            )
        data = json.loads(cached)
        await self.redis.delete(otp_keys,attempt_key,cooldown_key,otp_data_key)
        return data