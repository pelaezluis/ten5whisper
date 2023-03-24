from typing import Optional
from redis.asyncio import Redis
from uuid import uuid4 as uuid
from json import dumps, loads

redis_client = Redis()

async def add_prediction_to_redis(
    job_id: str,
    data: str
):  
    job_id = str(uuid())
    await redis_client.set(job_id, dumps(data))


async def get_prediction(job_id: str):
    exists = await redis_client.exists(job_id)
    if exists:
        prediction = await redis_client.get(job_id)
        print(prediction)
        return prediction
    return {'message': 'The job_id doesn\'t exist'}


async def delete_prediction(text: str):
    prediction = await redis_client.get(text)
    if prediction is not None:
        await redis_client.delete(text)