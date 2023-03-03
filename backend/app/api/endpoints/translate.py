from fastapi import APIRouter, Query

router = APIRouter()

@router.get('/check_translate/{job_id}')
async def check_translate(job_id: str = Query(...)):
    return {'translate': job_id}

@router.post('/translate_audio')
async def translate_audio():
    return {'audio': 'audio'}