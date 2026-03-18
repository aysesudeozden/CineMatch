import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.src.db_pg import engine, init_db, async_session_maker
from backend.src.recommender import engine as rec_engine
from backend.src.models_pg import Movie
from sqlalchemy.future import select

async def test():
    await init_db()
    
    print("Testing basic movie fetch (movies.py equivalent)...")
    async with async_session_maker() as session:
        result = await session.execute(select(Movie).limit(2))
        movies = result.scalars().all()
        # Test dict formatting just like the route does
        formatted = [{"_id": str(m.movieId), **{k: v for k, v in m.__dict__.items() if k != "_sa_instance_state"}} for m in movies]
        print(f"Success! Movies formatted: {[m['title'] for m in formatted]}")

    print("\nTesting Recommender Engine refresh (recommender.py equivalent)...")
    await rec_engine.refresh_data()
    print(f"Success! Recommender loaded {len(rec_engine.movies_df)} movies.")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
