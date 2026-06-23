from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
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
