from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    llm_model: str
    embedding_model: str
    groq_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()