from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Landmark
from .schemas import LandmarkResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Kursk 1000 API",
    description="Backend for Kursk 1000 mobile app",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/landmarks", response_model=list[LandmarkResponse])
def list_landmarks(db: Session = Depends(get_db)) -> list[LandmarkResponse]:
    """Все достопримечательности целиком — клиент кэширует это в Room."""
    landmarks = db.query(Landmark).order_by(Landmark.name).all()
    return [LandmarkResponse.from_landmark(lm) for lm in landmarks]


@app.get(
    "/landmark/{landmark_uuid}",
    response_model=LandmarkResponse,
    responses={404: {"description": "Landmark not found"}},
)
def get_landmark(landmark_uuid: UUID, db: Session = Depends(get_db)) -> LandmarkResponse:
    """Одна достопримечательность по UUID метки (регистр UUID не важен)."""
    landmark = db.get(Landmark, str(landmark_uuid).upper())
    if landmark is None:
        raise HTTPException(status_code=404, detail="Landmark not found")
    return LandmarkResponse.from_landmark(landmark)
