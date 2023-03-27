from typing import Optional
from redis.asyncio import Redis
from uuid import uuid4 as uuid
from json import dumps, loads
from app.core.deps import get_redis_client


async def add_prediction_to_redis(
    job_id: str,
    data: dict
):  
    redis_client: Redis = await get_redis_client()
    job_id = str(uuid())
    data = dumps(data)
    print(data)
    await redis_client.setex(job_id, 60000, data)


async def get_prediction(job_id: str):
    redis_client: Redis = await get_redis_client()
    exists = await redis_client.exists(job_id)
    if exists:
        prediction = await redis_client.get(job_id)
        print(prediction)
        return prediction
    return {'message': 'The job_id doesn\'t exist'}


async def delete_prediction(text: str):
    redis_client: Redis = await get_redis_client()
    prediction = await redis_client.get(text)
    if prediction is not None:
        await redis_client.delete(text)