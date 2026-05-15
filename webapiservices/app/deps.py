from fastapi import Depends, status, Query, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token
from app.utils.rate_limit import check_rate_limit
from app.utils.exceptions import AuthException, ErrorCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    user_id = decode_token(token)
    if user_id is None:
        raise AuthException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS[0],
            error_desc=ErrorCode.AUTH_INVALID_CREDENTIALS[1],
            status_code=status.HTTP_401_UNAUTHORIZED,
            debug_info="Could not validate credentials from token",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AuthException(
            error_code=ErrorCode.AUTH_USER_NOT_FOUND[0],
            error_desc=ErrorCode.AUTH_USER_NOT_FOUND[1],
            status_code=status.HTTP_401_UNAUTHORIZED,
            debug_info=f"User with id={user_id} not found in database",
        )
    if not user.is_active:
        raise AuthException(
            error_code=ErrorCode.AUTH_INACTIVE_USER[0],
            error_desc=ErrorCode.AUTH_INACTIVE_USER[1],
            status_code=status.HTTP_403_FORBIDDEN,
            debug_info=f"User '{user.username}' is inactive",
        )
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise AuthException(
            error_code=ErrorCode.AUTH_PERMISSION_DENIED[0],
            error_desc=ErrorCode.AUTH_PERMISSION_DENIED[1],
            status_code=status.HTTP_403_FORBIDDEN,
            debug_info="Admin privileges required for this operation",
        )
    return current_user


def get_current_user_or_api_key(
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
    api_key: str | None = Query(None),
) -> User:
    user = None
    if token:
        user_id = decode_token(token)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
    if user is None and api_key:
        user = db.query(User).filter(User.api_key == api_key).first()
    if user is None or not user.is_active:
        raise AuthException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS[0],
            error_desc=ErrorCode.AUTH_INVALID_CREDENTIALS[1],
            status_code=status.HTTP_401_UNAUTHORIZED,
            debug_info="Valid authentication (token or api_key) required",
        )
    return user


def rate_limit_read(request: Request):
    check_rate_limit(request, max_requests=60, window_seconds=60)


def rate_limit_write(request: Request):
    check_rate_limit(request, max_requests=30, window_seconds=60)


def rate_limit_auth(request: Request):
    check_rate_limit(request, max_requests=10, window_seconds=60)
