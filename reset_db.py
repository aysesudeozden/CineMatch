import asyncio
from backend.src.db_pg import engine, Base
import backend.src.models_pg

async def reset_db():
    async with engine.begin() as conn:
        print("Mevcut tablolar siliniyor...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Tablolar güncel şema ile yeniden oluşturuluyor...")
        await conn.run_sync(Base.metadata.create_all)
    print("Veritabanı başarıyla sıfırlandı.")

if __name__ == "__main__":
    asyncio.run(reset_db())
