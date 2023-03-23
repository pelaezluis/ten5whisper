from uuid import uuid4
from fastapi import APIRouter, Body, Query
from time import time
from app.api.celery_task import transcribe_audio_whisper

router = APIRouter()

@router.get('/check_translate/{job_id}')
async def check_translate(job_id: str = Query(...)):
    return {'translate': job_id}


@router.post('/translate_audio')
async def translate_audio(audio_path: str = Body(...)):
    job_id = uuid4()
    start = time()
    data = await transcribe_audio_whisper(audio_path)
    end = time()
    print(f'Translation took {end-start} seconds...')
    return data