from typing import AsyncIterator
from app.core.redis_manager import RedisManager
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

from redis.asyncio import Redis
import redis.asyncio as aioredis

import boto3
from botocore.client import BaseClient
from botocore.config import Config

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_redis() -> AsyncIterator[Redis]:
    pool = RedisManager()
    yield pool


async def SessionRedis():
    # Redis client bound to pool of connections (auto-reconnecting).
    return await aioredis.from_url(
        settings.CELERY_BROKER_URL, encoding="utf-8", decode_responses=True
    )


def s3_auth() -> BaseClient:
    my_config = Config(region_name=settings.AWS_BUCKET_REGION, signature_version="s3v4")

    s3 = boto3.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
        config=my_config,
    )
    return s3
