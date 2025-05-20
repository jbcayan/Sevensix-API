import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load environment variables from .env file
load_dotenv()


# Define BASE_DIR - path to the project root directory
# This goes up 3 levels from the settings.py file to reach the project root
# settings.py is in app/config/settings.py, so we need to go up 3 levels
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --------------------------------------------------------------------------- #
# CONFIGURATION
# --------------------------------------------------------------------------- #
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

    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")  # <-- Add this line

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

    # --------------------------------------------------------------------------- #
    # LLM MODEL CONFIGS                                                                                                                          #
    # --------------------------------------------------------------------------- #

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        validate_by_name = True
        extra = "ignore"

settings = Settings()

# 3. Instantiate OpenAI client(s) USING the loaded API key
#    and OUTSIDE the Settings config class to keep Pydantic happy.
public_chat_model = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY  # <-- Here it is injected
)
private_chat_model = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/login")
