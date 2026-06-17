from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Landmark
from .schemas import HealthResponse, LandmarkResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Kursk 1000 API",
    description="Backend for Kursk 1000 mobile app",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/landmarks", response_model=list[LandmarkResponse])
def list_landmarks(db: Session = Depends(get_db)) -> list[Landmark]:
    return db.query(Landmark).order_by(Landmark.name).all()


@app.get("/landmark/{landmark_uuid}", response_model=LandmarkResponse)
def get_landmark(landmark_uuid: UUID, db: Session = Depends(get_db)) -> Landmark:
    landmark = db.get(Landmark, str(landmark_uuid).upper())
    if landmark is None:
        raise HTTPException(status_code=404, detail="Landmark not found")
    return landmark