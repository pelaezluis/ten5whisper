from fastapi import FastAPI
from app.api import api
from contextlib import asynccontextmanager
import whisper


MODEL = 'base'
model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f'Loading {MODEL} model')
    model['whisper'] = whisper.load_model(MODEL)
    yield
    print('Shutting down the model...')


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return {'message': 'Server is running'}


app.include_router(api.router, )