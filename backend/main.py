"""
CineMatch FastAPI Backend
MongoDB ile film öneri sistemi backend API'si
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# MongoDB bağlantı fonksiyonları
from mongodb import connect_to_mongo, close_mongo_connection

# Route'ları import et
from routes import users, movies, interactions, genres, chat, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış olayları"""
    # Başlangıç
    await connect_to_mongo()
    # Öneri motorunu hazırla
    from src.recommender import engine
    import asyncio
    asyncio.create_task(engine.refresh_data())
    yield
    # Kapanış
    await close_mongo_connection()


# FastAPI uygulaması oluştur
app = FastAPI(
    title="CineMatch API",
    description="Film öneri sistemi için MongoDB tabanlı REST API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware ekle (frontend ile iletişim için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route'ları ekle
app.include_router(users.router)
app.include_router(movies.router)
app.include_router(interactions.router)
app.include_router(genres.router)
app.include_router(chat.router)
app.include_router(recommendations.router)


@app.get("/")
async def root():
    """Ana endpoint - API durumu"""
    return {
        "message": "CineMatch API çalışıyor! 🎬",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    return {"status": "healthy", "service": "CineMatch API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )