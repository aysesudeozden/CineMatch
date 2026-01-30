"""
MongoDB bağlantı modülü
Motor (async MongoDB driver) kullanarak asenkron veritabanı işlemleri yapar
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# .env dosyasını yükle (Root dizininden)
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# MongoDB bağlantı URL'si
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = "CineMatch_db"

# Global MongoDB client ve database nesneleri
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """MongoDB'ye bağlantı kur"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        database = client[DATABASE_NAME]
        # Bağlantıyı test et
        await client.admin.command('ping')
        print(f"MongoDB'ye başarıyla bağlanıldı: {DATABASE_NAME}")
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {e}")
        raise


async def close_mongo_connection():
    """MongoDB bağlantısını kapat"""
    global client
    if client:
        client.close()
        print("🔌 MongoDB bağlantısı kapatıldı")


def get_database():
    """Database nesnesini döndür"""
    return database


# Koleksiyon erişim fonksiyonları
def get_users_collection():
    """Users koleksiyonunu döndür"""
    return database.users


def get_movies_collection():
    """Movies koleksiyonunu döndür"""
    return database.movies


def get_genres_collection():
    """Genres koleksiyonunu döndür"""
    return database.genres


def get_movie_genres_collection():
    """Movie_genres koleksiyonunu döndür"""
    return database.movie_genres


def get_user_interactions_collection():
    """User_interactions koleksiyonunu döndür"""
    return database.user_interactions
