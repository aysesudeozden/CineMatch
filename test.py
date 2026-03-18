import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.db_pg import SessionLocal
from backend.routes.movies import get_all_movies

async def main():
    async with SessionLocal() as db:
        try:
            print("Testing with genre_ids='12'...")
            movies = await get_all_movies(skip=0, limit=10, search=None, genre_ids="12", sort_by=None, db=db)
            print(f"Got {len(movies)} movies.")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
