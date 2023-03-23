import gc
from typing import Any
from fastapi import FastAPI
from app.api import api
from contextlib import asynccontextmanager
import whisper
from app.core.config import settings
#
from app.utils.fastapi_globals import g, GlobalsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    models: dict[str, Any] = {"whisper_model": whisper.load_model(settings.MODEL_NAME)}
    print(f"Loading {settings.MODEL_NAME} model")
    g.set_default("whisper_model", models["whisper_model"])
    print("Model loaded...")
    yield
    models.clear()
    g.cleanup()
    gc.collect()
    print("Model cleaned...")


app = FastAPI(lifespan=lifespan)
# app = FastAPI()

app.add_middleware(GlobalsMiddleware)


@app.get("/")
async def root():
    return {"message": "Server is running"}


app.include_router(api.router)
