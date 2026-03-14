import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
import sys

# Add root to pythonpath
sys.path.append(str(Path(__file__).parent.parent))

from backend.src.models_pg import Base

async def reset_database():
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        if "?" in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.split("?")[0]
            
    engine = create_async_engine(
        DATABASE_URL, 
        echo=False,
        connect_args={"ssl": "require"}
    )
    
    print("Tablolar siliniyor...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    print("Yeniden oluşturuluyor...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    await engine.dispose()
    print("Veritabanı sıfırlandı!")

if __name__ == "__main__":
    asyncio.run(reset_database())
