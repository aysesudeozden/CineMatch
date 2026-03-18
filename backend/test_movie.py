import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.src.db_pg import engine, init_db, async_session_maker
from backend.src.models_pg import Movie
from sqlalchemy.future import select

async def test():
    await init_db()
    async with async_session_maker() as session:
        res = await session.execute(select(Movie).limit(1))
        movie = res.scalars().first()
        if movie:
            print(f"Success! Found movie: {movie.title} (movieId: {movie.movieId})")
        else:
            print("No movie found, but query succeeded.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
