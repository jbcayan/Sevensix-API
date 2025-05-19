from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.services.auth import verify_token_async
from app.accounts.models.user import User, RoleEnum
from app.config.database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token_data = await verify_token_async(token)
    if not token_data or token_data.user_id is None:
        raise _credentials_exc()

    stmt = select(User).where(User.id == token_data.user_id)
    result = await db.execute(stmt)
    user: User | None = result.scalars().first()
    if user is None:
        raise _credentials_exc()
    return user

def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

def _credentials_exc() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )