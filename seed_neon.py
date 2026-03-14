import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# asyncpg yerine psycopg2 kullanıyoruz pandas entegrasyonu için
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
engine = create_engine(DATABASE_URL)

base_path = "backend/data"

def seed_db():
    print("Veritabanı bağlantısı kuruldu.")
    
    # 1. Genres tablosunu yükle
    print("Türler (Genres) yükleniyor...")
    genres_df = pd.read_csv(f"{base_path}/genres.csv")
    # Mevcut veriyi silmek yerine append yapmak daha güvenli. Ancak ID çakışması varsa hata verir.
    # O yüzden basitçe to_sql
    try:
        genres_df.to_sql("genres", engine, if_exists="append", index=False)
        print("Türler başarıyla yüklendi.")
    except Exception as e:
        print(f"Türler yüklenirken hata oluştu (belki zaten yüklü): {e}")

    valid_movie_ids = []
    
    # 2. Movies tablosunu yükle
    print("Filmler (Movies) yükleniyor... Bu işlem veri boyutuna göre zaman alabilir.")
    try:
        movies_df = pd.read_csv(f"{base_path}/movies_with_metadata.csv")
        # CSV sütunlarını model'e göre yeniden adlandır veya seç
        # Model alanları: movieId, title, original_title, original_language, popularity, release_date, runtime, vote_average, rating_count, poster_url, overview, llm_metadata
        
        # 'movie_id' -> 'movieId'
        movies_df = movies_df.rename(columns={"movie_id": "movieId"})
        
        # Fazla sütunları dışla (örneğin imdbid, tmdbid)
        valid_columns = ["movieId", "title", "original_title", "original_language", 
                         "popularity", "release_date", "runtime", "vote_average", 
                         "rating_count", "poster_url", "llm_metadata"]
        
        movies_to_insert = movies_df[[col for col in valid_columns if col in movies_df.columns]].copy()
        
        movies_to_insert.to_sql("movies", engine, if_exists="append", index=False)
        valid_movie_ids = movies_to_insert["movieId"].tolist()
        print(f"Filmler başarıyla yüklendi. ({len(movies_to_insert)} satır)")
    except Exception as e:
        print(f"Filmler yüklenirken hata oluştu: {e}")

    # 3. Movie-Genres ilişkisini yükle
    print("Film-Tür (Movie-Genres) ilişkileri yükleniyor...")
    try:
        mg_df = pd.read_csv(f"{base_path}/movie_genres.csv")
        if 'movieId' in mg_df.columns:
            mg_df = mg_df.rename(columns={'movieId': 'movie_id'})
            
        # Foreign Key kuralı ihlali için, veritabanına eklenmemiş filmlerin türlerini temizle
        if valid_movie_ids:
            initial_len = len(mg_df)
            mg_df = mg_df[mg_df["movie_id"].isin(valid_movie_ids)]
            print(f"Yetim (Foreign Key uymayan) ilişkiler temizlendi: {initial_len - len(mg_df)} satır.")
            
        mg_df.to_sql("movie_genres", engine, if_exists="append", index=False)
        print(f"Film-Tür ilişkisi başarıyla yüklendi. ({len(mg_df)} satır)")
    except Exception as e:
        print(f"Film-Tür ilişkisi yüklenirken hata oluştu: {e}")

if __name__ == "__main__":
    seed_db()
