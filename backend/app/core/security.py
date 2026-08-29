import jwt
from pwdlib import PasswordHash
from app.core.config import setting
import uuid
from typing import Optional, Any, Dict, Union
from datetime import datetime, timezone, timedelta

password_hash = PasswordHash.recommended()

def hash_password(plain_password: str):
    return password_hash.hash(password=plain_password)

def varify_password(plain_password: str,hash_passwords: str):
    return password_hash.verify(password=plain_password,hash=hash_passwords)

def create_access_token(data: str|uuid.UUID, extra_claims: Optional[Union[str,Any]]=None)->str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=setting.ACCESS_TOKEN_EXPIRY_TIME)
    to_encode: Dict[str,Any] = {
        "sub":str(data),
        "exp":expire,
        "type":"access",
        "iat":datetime.now(timezone.utc)
    }
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode,setting.SECRET_KEY,setting.ALGORITHM)

def create_referesh_token(data: str|uuid.UUID)->str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=setting.REFERESH_EXPIRY_TIME)
    to_encode = {
        "sub":str(data),
        "exp":expire,
        "type":"refresh",
        "iat":datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode,setting.REFERESH_SECRET_KEY,setting.REFERESH_EXPIRY_TIME)

def decode_token(token: str, is_refresh: bool = False)->Optional[Dict[str, Any]]:
    key = setting.REFERESH_SECRET_KEY if is_refresh else setting.SECRET_KEY
    try:
        payload = jwt.decode(token,key,[setting.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None