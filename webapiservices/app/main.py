from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, users, poi

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LBS POI Web API",
    description="基于位置的服务 - 专题 POI Web API",
    version="1.0.0",
)

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
