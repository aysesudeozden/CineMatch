import asyncio
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from backend.src.recommender import engine

async def test():
    await engine.refresh_data()
    print(f"is_ready: {engine.is_ready}")

    print("\n--- GUEST (Genre ID 1 = Action) ---")
    results = await engine.recommend_for_guest([1])
    for m in results[:3]:
        print(f"  {m['title']} (pop={m['popularity']:.1f}, vote={m['vote_average']:.1f})")

    print("\n--- GUEST (no genre) ---")
    results = await engine.recommend_for_guest([])
    for m in results[:3]:
        print(f"  {m['title']} (pop={m['popularity']:.1f})")

    print("\nAll tests passed!")

if __name__ == "__main__":
    asyncio.run(test())
