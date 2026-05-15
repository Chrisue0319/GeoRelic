from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import auth, users, poi
from app.utils.security import decode_token
from app.utils.exceptions import ServiceException
from app.utils.error_handler import (
    service_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
)

Base.metadata.create_all(bind=engine)


def _rate_limit_key(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        user_id = decode_token(token)
        if user_id:
            return f"user:{user_id}"
    api_key = request.query_params.get("api_key")
    if api_key:
        return f"apikey:{api_key[:16]}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


limiter = Limiter(key_func=_rate_limit_key)

app = FastAPI(
    title="LBS POI Web API",
    description="基于位置的服务 - 专题 POI Web API",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(ServiceException, service_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(poi.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "LBS POI Web API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
