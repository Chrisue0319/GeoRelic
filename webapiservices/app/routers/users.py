from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.utils.security import generate_api_key, get_password_hash

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserSchema)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_in.email is not None:
        existing = db.query(User).filter(User.email == user_in.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_in.email
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/api-key", response_model=dict)
def generate_user_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.api_key = generate_api_key()
    from datetime import datetime
    current_user.api_key_created_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return {"api_key": current_user.api_key}
