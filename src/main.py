
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .url_shortner.routes import router as url_shortner
from .url_shortner.models import Link  # noqa
from src.database import init_db
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, title=settings.PROJECT_NAME)
app.include_router(url_shortner, prefix="", tags=["URL shortner"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_type = exc.errors()[0]["type"]
    loc = exc.errors()[0]["loc"]


    match (error_type, loc):
        case (_, ["body", "shortcode"]):
            return JSONResponse(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                content={"message": "The provided shortcode is invalid"}
            )
        
        case ("missing", ["body", "url"]):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Url not present"}
            )
        
        case (_, ["body", "url"]):
            return JSONResponse(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                content={"message": "The rpovided url is invalid"}
            )
        
        case _:
            return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Validation error", "details": exc.errors()}
        )
