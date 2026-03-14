import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from pathlib import Path

async def test_conn():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    if "?" in url:
        base_url, query = url.split("?", 1)
        import urllib.parse
        params = urllib.parse.parse_qs(query)
        params.pop('sslmode', None)
        params.pop('channel_binding', None)
        new_query = urllib.parse.urlencode(params, doseq=True)
        url = f"{base_url}?{new_query}" if new_query else base_url
    
    print(f"Testing connection to: {url[:20]}...")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    from sqlalchemy import text
    asyncio.run(test_conn())
