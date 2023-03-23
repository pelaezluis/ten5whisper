from typing import List, Union
import os
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    validator
)
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    API_V1                : str = "/api/v1"
    SERVER_NAME           : str = os.environ["SERVER_NAME"]
    PROJECT_NAME          : str
    CELERY_BROKER_URL     : str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
    CELERY_RESULT_BACKEND : str
    BACKEND_CORS_ORIGINS  : Union[List[str], List[AnyHttpUrl]]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = os.path.expanduser("~/.env")


settings = Settings()
