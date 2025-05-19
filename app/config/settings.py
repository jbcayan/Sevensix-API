import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(10080, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    DATABASE_TYPE: str = Field("sqlite3", env="DATABASE_TYPE")
    SQLITE_DB_PATH: str = Field("./app.db", env="SQLITE_DB_PATH")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: str = Field("5432", env="POSTGRES_PORT")
    POSTGRES_USER: str = Field("user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("password", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("db", env="POSTGRES_DB")

    ALLOWED_ORIGINS_RAW: str = Field("http://localhost,http://localhost:3000", alias="ALLOWED_ORIGINS")

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_RAW.split(",") if origin.strip()]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_TYPE.lower() == "postgres":
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return f"sqlite:///{self.SQLITE_DB_PATH}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        validate_by_name = True
        extra = "ignore"

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/login")
