import secrets
from sqlalchemy import select
from sqlalchemy.future import select as async_select

import jwt
from datetime import datetime, timedelta


from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession


from config import SECRET
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException

from database import get_async_session

algorithm = 'HS256'
security = HTTPBearer()


def generate_token(user_id: int):
    jti_access = secrets.token_urlsafe(32)
    jti_refresh = secrets.token_urlsafe(32)

    payload_access = {
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'user_id': user_id,
        'jti': jti_access,
    }
    payload_refresh = {
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=1),
        'user_id': user_id,
        'jti': jti_refresh,
    }
    access_token = jwt.encode(payload_access, SECRET, algorithm=algorithm)
    refresh_token = jwt.encode(payload_refresh, SECRET, algorithm=algorithm)
    return {
        'access': access_token,
        'refresh': refresh_token
    }


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token is expired!')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Token invalid!')

