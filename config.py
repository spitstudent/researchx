from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    gemini_api_key:str
    serp_api_key:str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()