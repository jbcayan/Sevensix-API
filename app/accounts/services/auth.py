import asyncio
from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext

from app.accounts.models.user import RoleEnum
from app.accounts.schemas.users import TokenData
from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Define your secret key and algorithm

def create_access_token(
    user_id: int,
    role: RoleEnum,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = {
        "sub": str(user_id),
        "role": role.value,
        "exp": datetime.utcnow() + (expires_delta or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if not sub:
            return None
        return TokenData(user_id=int(sub), role=RoleEnum(role) if role else None)
    except (jwt.PyJWTError, ValueError):
        return None

async def verify_token_async(token: str) -> Optional[TokenData]:
    return await asyncio.to_thread(verify_token, token)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
