import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import sys

# Add root to pythonpath
sys.path.append(str(Path(__file__).parent.parent))

from backend.src.models_pg import Base, Genre, Movie, MovieGenre

async def seed_database():
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("HATA: DATABASE_URL .env dosyasında bulunamadı!")
        return
        
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg'de query parametresi olan sslmode bazen desteklenmeyebilir.
        if "?" in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.split("?")[0]
            
    print(f"Bağlanılan veritabanı: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Bilinmiyor'}")
    
    # SSL require için connect_args üzerinden ayarlama yapmak daha güvenlidir
    engine = create_async_engine(
        DATABASE_URL, 
        echo=False,
        connect_args={"ssl": "require"}
    )
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # 1. Tabloları oluştur (Eğer yoksa)
    print("Tablolar kontrol ediliyor...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    data_dir = Path(__file__).parent.parent / "backend" / "data"
    
    async with async_session() as session:
        # --- 2. Türleri (Genres) Yükle ---
        genres_path = data_dir / "genres.csv"
        if genres_path.exists():
            print(f"{genres_path.name} okunuyor...")
            genres_df = pd.read_csv(genres_path)
            
            # Var olan kayıtları silmeden ekleme mantığı
            existing_genres = await session.execute(Base.metadata.tables['genres'].select())
            existing_genre_ids = {row[0] for row in existing_genres}
            
            genres_to_add = []
            for _, row in genres_df.iterrows():
                if row['genre_id'] not in existing_genre_ids:
                    genres_to_add.append(Genre(genre_id=row['genre_id'], genre_name=row['genre_name']))
            
            if genres_to_add:
                session.add_all(genres_to_add)
                await session.commit()
                print(f"{len(genres_to_add)} yeni tür eklendi.")
            else:
                print("Türler zaten güncel.")
        else:
            print(f"HATA: {genres_path} bulunamadı!")

        # --- 3. Filmleri (Movies) Yükle ---
        # movies_with_metadata.csv varsa onu kullan, yoksa movies (1).csv
        movies_meta_path = data_dir / "movies_with_metadata.csv"
        movies_basic_path = data_dir / "movies (1).csv"
        
        movies_df = None
        if movies_meta_path.exists():
            print(f"{movies_meta_path.name} okunuyor...")
            movies_df = pd.read_csv(movies_meta_path)
        elif movies_basic_path.exists():
            print(f"{movies_basic_path.name} okunuyor...")
            movies_df = pd.read_csv(movies_basic_path)
        
        if movies_df is not None:
            existing_movies = await session.execute(Base.metadata.tables['movies'].select())
            # index 1 veya movieId mappingine bakaşım
            movie_ids = {row[1] for row in existing_movies} # index 1 movieId'dir genelde
            
            movies_to_add = []
            count = 0
            for _, row in movies_df.iterrows():
                m_id = row.get('movieId') or row.get('id')
                if pd.isna(m_id):
                    continue
                m_id = int(m_id)
                
                if m_id not in movie_ids:
                    movie = Movie(
                        movieId=m_id,
                        title=row.get('title', ''),
                        original_title=row.get('original_title') if pd.notna(row.get('original_title')) else None,
                        original_language=row.get('original_language') if pd.notna(row.get('original_language')) else None,
                        popularity=float(row.get('popularity')) if pd.notna(row.get('popularity')) else 0.0,
                        release_date=str(row.get('release_date')) if pd.notna(row.get('release_date')) else None,
                        vote_average=float(row.get('vote_average')) if pd.notna(row.get('vote_average')) else 0.0,
                        poster_url=row.get('poster_url') if pd.notna(row.get('poster_url')) else None,
                        llm_metadata=row.get('llm_metadata') if pd.notna(row.get('llm_metadata')) else None
                    )
                    movies_to_add.append(movie)
                    movie_ids.add(m_id)
                    count += 1
                    
                    # Batch commit for memory efficiency
                    if len(movies_to_add) >= 500:
                        session.add_all(movies_to_add)
                        await session.commit()
                        movies_to_add = []
            
            if movies_to_add:
                session.add_all(movies_to_add)
                await session.commit()
            print(f"{count} film PostgreSQL'e aktarıldı.")
            
        else:
            print("HATA: Film verisi bulunamadı!")
            
        # --- 4. Film - Tür İlişkilerini (Movie_Genres) Yükle ---
        mg_path = data_dir / "movie_genres.csv"
        if mg_path.exists():
            print(f"{mg_path.name} okunuyor...")
            mg_df = pd.read_csv(mg_path)
            
            # Çok fazla ilişkisi olacağı için direkt insert_many veya teker teker
            # Sadece eşleşen movieId'leri alalım
            valid_movies = movie_ids
            
            # Performans için eğer tablo boşsa dolduralım, değilse atlayalım (gerçekte daha kompleks kontrol gerekir)
            result = await session.execute(Base.metadata.tables['movie_genres'].select().limit(1))
            if not result.first():
                relations = []
                for _, row in mg_df.iterrows():
                    m_id = row.get('movie_id')
                    g_id = row.get('genre_id')
                    
                    if pd.notna(m_id) and pd.notna(g_id) and int(m_id) in valid_movies:
                        relations.append(MovieGenre(movie_id=int(m_id), genre_id=int(g_id)))
                        
                        if len(relations) >= 1000:
                            session.add_all(relations)
                            await session.commit()
                            relations = []
                            
                if relations:
                    session.add_all(relations)
                    await session.commit()
                print("Film-Tür ilişkileri eklendi.")
            else:
                print("Film-Tür ilişkileri halihazırda veritabanında mevcut.")
                

    await engine.dispose()
    print("Veri aktarımı tamamlandı!")

if __name__ == "__main__":
    asyncio.run(seed_database())
