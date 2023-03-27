from uuid import uuid4
from fastapi import APIRouter, Body, Query
from app.schemas.response_schema import IGetResponseBase, IPostResponseBase, create_response
from app.utils.storage_redis import get_prediction
from app.api.celery_task import transcribe_voice_message
from app.api.celery_task import transcribe_audio_whisper
from app.utils.fastapi_globals import g

router = APIRouter()


@router.get("/check_translate/{job_id}", response_model=IGetResponseBase[dict])
async def check_translate(job_id: str = Query(...)):
    data = await get_prediction(job_id)
    return create_response(data={"translate": data})


@router.post("/translate_audio", response_model=IPostResponseBase[dict])
async def translate_audio(audio_path: str = Body(...)):
    job_id = str(uuid4())
    transcribe_voice_message.delay(audio_path, job_id, model=g.whisper_model)
    return create_response(data={'job_id': job_id})
