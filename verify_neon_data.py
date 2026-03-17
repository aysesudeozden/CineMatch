import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from pathlib import Path

async def verify_data():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not found")
        return

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
    
    print(f"Connecting to database...")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            # Check movies count
            movie_count = await conn.execute(text("SELECT COUNT(*) FROM movies"))
            count = movie_count.scalar()
            print(f"Movie count: {count}")
            
            if count > 0:
                # Fetch first 5 movie titles
                sample_movies = await conn.execute(text("SELECT title FROM movies LIMIT 5"))
                print("Sample movies:")
                for row in sample_movies:
                    print(f"- {row[0]}")
            else:
                print("WARNING: Database is empty!")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_data())
