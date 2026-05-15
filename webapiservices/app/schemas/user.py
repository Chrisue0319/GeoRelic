from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    api_key: str | None = None
    api_key_created_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int | None = None
