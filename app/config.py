import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ccms_db")
    
    # Qdrant Vector DB
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = "court_judgments"
    
    # Embedding Models
    DENSE_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL_NAME: str = "prithivida/Splade_PP_en_v1" # Generates sparse lexical vectors
    
    # Paths
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)