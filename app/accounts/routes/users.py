
# app/accounts/routes/users.py

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, Select
from sqlalchemy.exc import IntegrityError

from app.accounts.models.user import User, RoleEnum
from app.accounts.permissions import admin_required
from app.accounts.schemas.users import UserCreate, UserOut, UserLogin, Token
from app.accounts.services.auth import create_access_token
from app.config.database import get_db
from app.config.settings import settings


# --------------------------------------------------------------------------- #
# Shared utilities                                                            #
# --------------------------------------------------------------------------- #
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _hash(password: str) -> str:
    return pwd_context.hash(password)

def _verify(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

async def _duplicated(
    db: AsyncSession,
    *,
    username: str | None = None,
    email: str | None = None,
    exclude_id: int | None = None,
) -> bool:
    """
    Return True if another row matches username or email.
    """
    conds = []
    if username:
        conds.append(User.username == username)
    if email:
        conds.append(User.email == email)
    if not conds:
        return False
    stmt = select(User.id).where(or_(*conds))
    if exclude_id:
        stmt = stmt.where(User.id != exclude_id)
    return (await db.execute(stmt)).scalars().first() is not None


@router.post("/register", response_model=UserOut)
async def create_user(
    new_user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    if await _duplicated(db, username=new_user.username, email=new_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    user = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=_hash(new_user.password),
        role=new_user.role or RoleEnum.MODERATOR,
    )
    db.add(user)
    try:
        await db.commit()  # Save user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    await db.refresh(user)
    return user


# --------------------------------------------------------------------------- #
# Public route: login                                                         #
# --------------------------------------------------------------------------- #
@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    res = await db.execute(stmt)
    db_user: User | None = res.scalars().first()

    if not db_user or not _verify(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user_id=db_user.id,
        role=db_user.role,
        expires_delta=expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}



# --------------------------------------------------------------------------- #
# Admin‑only routes: user CRUD                                                #
# --------------------------------------------------------------------------- #
admin_router = APIRouter(
    prefix="/users",
    dependencies=[Depends(admin_required)],
)

@admin_router.get("", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    return res.scalars().all()
