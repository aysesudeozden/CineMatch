"""
Kullanıcı API endpoint'leri
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
import bcrypt
import os

from backend.src.db_pg import get_db
from backend.src.models_pg import User, Interaction
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/users", tags=["users"])


def _hash_password(plain: str) -> str:
    """Düz metin şifreyi bcrypt ile hashle."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def _verify_password(plain: str, stored: str) -> bool:
    """Şifreyi doğrula. Hem hash hem düz metin desteklenir (soft migration)."""
    # Eğer stored bir bcrypt hash ise
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        return bcrypt.checkpw(plain.encode(), stored.encode())
    # Eski düz metin — eşleşiyorsa True döner (login sonrası hashlenecek)
    return plain == stored


@router.get("")
async def get_all_users(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Tüm kullanıcıları getir (Admin API key ile korumalı)"""
    admin_key = request.headers.get("X-Admin-Key", "")
    expected = os.environ.get("ADMIN_API_KEY", "")
    if not expected or admin_key != expected:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim.")
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return [
            {
                "_id": str(u.id),
                **{k: v for k, v in u.__dict__.items()
                   if k not in ("_sa_instance_state", "password")}
            }
            for u in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcılar getirilirken hata: {str(e)}")


@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Belirli bir kullanıcıyı getir"""
    try:
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail=f"Kullanıcı bulunamadı: {user_id}")

        user_dict = {k: v for k, v in user.__dict__.items()
                     if k not in ("_sa_instance_state", "password")}
        return {"_id": str(user.id), **user_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı getirilirken hata: {str(e)}")


@router.post("/auth/register")
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Yeni kullanıcı oluştur (Benzersiz email ve şifre ile)"""
    try:
        email = (user_data.get("email") or "").strip().lower()
        password = user_data.get("password") or ""
        full_name = (user_data.get("full_name") or "").strip()

        # Temel validasyon
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise HTTPException(status_code=400, detail="Geçerli bir email adresi giriniz.")
        if not password or len(password) < 8:
            raise HTTPException(status_code=400, detail="Şifre en az 8 karakter olmalıdır.")
        if not full_name:
            raise HTTPException(status_code=400, detail="Ad soyad zorunludur.")

        # Email tekrar kontrolü
        result = await db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Bu email adresi zaten kullanımda.")

        # Yeni user_id
        result = await db.execute(select(User).order_by(User.user_id.desc()).limit(1))
        last_user = result.scalars().first()
        new_id = (last_user.user_id + 1) if last_user and last_user.user_id else 1

        # Şifreyi hashle
        hashed_password = _hash_password(password)

        new_user = User(
            user_id=new_id,
            full_name=full_name,
            email=email,
            password=hashed_password,
            selected_genres=user_data.get("selected_genres", [])
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Başlangıç interaction kaydı
        new_int = Interaction(
            interaction_id=new_id * 1000,
            user_id=new_id,
            movie_id=0,
            is_liked=False,
            rating=0.0
        )
        db.add(new_int)
        await db.commit()

        user_dict = {k: v for k, v in new_user.__dict__.items()
                     if k not in ("_sa_instance_state", "password")}
        return {"status": "success", "user_id": new_id, "user": {"_id": str(new_user.id), **user_dict}}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Kayıt sırasında hata: {str(e)}")


@router.post("/auth/login")
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    login_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Email ve şifre ile giriş yap"""
    try:
        email = (login_data.get("email") or "").strip().lower()
        password = login_data.get("password") or ""

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email ve şifre zorunludur.")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        # Genel hata mesajı — hangi bilginin yanlış olduğunu belli etme
        if not user or not _verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Email veya şifre hatalı.")

        # Soft migration: düz metin şifreyse hashle ve kaydet
        if not (user.password.startswith("$2b$") or user.password.startswith("$2a$")):
            user.password = _hash_password(password)
            await db.commit()

        user_dict = {k: v for k, v in user.__dict__.items()
                     if k not in ("_sa_instance_state", "password")}
        return {"status": "success", "user": {"_id": str(user.id), **user_dict}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Giriş sırasında hata: {str(e)}")


@router.post("/{user_id}/preferences")
async def save_user_preferences(
    user_id: int,
    preferences: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcının seçtiği türleri kaydet"""
    try:
        selected_genres = preferences.get("selected_genres", [])

        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        if user:
            user.selected_genres = selected_genres

        await db.commit()
        return {"status": "success", "message": "Tercihler kaydedildi"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Tercihler kaydedilirken hata: {str(e)}")
