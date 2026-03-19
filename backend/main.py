"""
CineMatch FastAPI Backend
PostgreSQL (Neon.tech) ile film öneri sistemi backend API'si
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# PostgreSQL bağlantı fonksiyonları
from backend.src.db_pg import init_db, close_db

# Route'ları import et
from backend.routes import users, movies, interactions, genres, chat, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış olayları"""
    await init_db()
    yield
    await close_db()


# FastAPI uygulaması oluştur
app = FastAPI(
    title="CineMatch API",
    description="Film öneri sistemi için PostgreSQL tabanlı REST API",
    version="1.0.0",
    lifespan=lifespan
)

# slowapi rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware — sadece bilinen origin'lere izin ver
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    os.environ.get("NEXT_PUBLIC_APP_URL", ""),          # Vercel URL (env'den)
    "https://cine-match-gamma.vercel.app",              # Vercel production URL
]
# Boş string'leri temizle
ALLOWED_ORIGINS = [o for o in ALLOWED_ORIGINS if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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