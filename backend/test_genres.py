import asyncio
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.src.db_pg import engine, init_db, async_session_maker
from sqlalchemy import text

async def test():
    await init_db()
    async with async_session_maker() as session:
        # Check actual columns in movie_genres
        res = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'movie_genres';"))
        print("Columns in 'movie_genres':", [r[0] for r in res.fetchall()])

        # Sample rows from movie_genres
        res2 = await session.execute(text("SELECT * FROM movie_genres LIMIT 5;"))
        print("\nSample rows:")
        for row in res2.fetchall():
            print(row)

        # Check the count
        res3 = await session.execute(text("SELECT COUNT(*) FROM movie_genres;"))
        print("\nTotal movie_genres rows:", res3.scalar())

        # Get genre_ids that have entries in movie_genres
        res4 = await session.execute(text("SELECT DISTINCT genre_id FROM movie_genres LIMIT 10;"))
        print("\nSample genre_ids in movie_genres:", [r[0] for r in res4.fetchall()])

        # Get movies that are in genre 1 (Action typically)
        res5 = await session.execute(text("SELECT movie_id FROM movie_genres WHERE genre_id = 1 LIMIT 5;"))
        print("\nMovies in genre_id=1:", [r[0] for r in res5.fetchall()])

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
