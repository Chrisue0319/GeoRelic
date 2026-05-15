from datetime import timedelta
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import rate_limit_auth
from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.utils.exceptions import AuthException, ErrorCode

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=Token)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _rate_limit=Depends(rate_limit_auth),
):
    if db.query(User).filter(User.username == user_in.username).first():
        raise AuthException(
            error_code=ErrorCode.AUTH_USERNAME_EXISTS[0],
            error_desc=ErrorCode.AUTH_USERNAME_EXISTS[1],
            status_code=status.HTTP_400_BAD_REQUEST,
            debug_info=f"Username '{user_in.username}' is already taken",
        )
    if db.query(User).filter(User.email == user_in.email).first():
        raise AuthException(
            error_code=ErrorCode.AUTH_EMAIL_EXISTS[0],
            error_desc=ErrorCode.AUTH_EMAIL_EXISTS[1],
            status_code=status.HTTP_400_BAD_REQUEST,
            debug_info=f"Email '{user_in.email}' is already registered",
        )
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _rate_limit=Depends(rate_limit_auth),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS[0],
            error_desc=ErrorCode.AUTH_INVALID_CREDENTIALS[1],
            status_code=status.HTTP_401_UNAUTHORIZED,
            debug_info="Incorrect username or password",
        )
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
