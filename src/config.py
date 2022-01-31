from pydantic import BaseSettings


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str
    AWS_REGION: str
    AWS_S3_BUCKET_NAME: str
    DB_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    
    class Config:
        env_file = ".env"