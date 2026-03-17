"""
CineMatch FastAPI Backend
PostgreSQL (Neon.tech) ile film öneri sistemi backend API'si
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# PostgreSQL bağlantı fonksiyonları
from backend.src.db_pg import init_db, close_db

# Route'ları import et
from backend.routes import users, movies, interactions, genres, chat, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış olayları"""
    # Başlangıç
    await init_db()
    # Öneri motorunu burada başlatmıyoruz (Vercel memory/timeout sınırları için)
    # İlk kullanımda (lazy-loading) yüklenecek.
    yield
    
    # Kapanış
    await close_db()


# FastAPI uygulaması oluştur
app = FastAPI(
    title="CineMatch API",
    description="Film öneri sistemi için PostgreSQL tabanlı REST API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware ekle (frontend ile iletişim için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vercel deployment ve local için geniş izin
    allow_credentials=False, # allow_origins="*" ise bu False olmalı
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