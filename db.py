from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, JSON, DateTime, func
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from config import settings

Base = declarative_base()

# Application Data Models (SQLAlchemy)
class DocumentState(Base):
    __tablename__ = "document_states"
    
    doc_id = Column(String, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    extracted_data = Column(JSON, nullable=True) # Stores the final Action Plan
    status = Column(String, default="PROCESSING") # PROCESSING, PENDING_REVIEW, VERIFIED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Async SQLAlchemy Engine for App Data
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Async Postgres Pool for LangGraph Checkpointing
# LangGraph uses raw psycopg connections rather than SQLAlchemy for state saving
checkpointer_pool = AsyncConnectionPool(
    conninfo=settings.DATABASE_URL.replace("+asyncpg", ""), 
    max_size=20
)

async def get_checkpointer():
    """Yields the LangGraph checkpointer configured with the connection pool."""
    saver = AsyncPostgresSaver(checkpointer_pool)
    await saver.setup() # Ensures checkpointer tables exist
    return saver

async def init_db():
    """Initializes Application tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)