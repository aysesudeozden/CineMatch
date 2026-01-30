"""
Kullanıcı API endpoint'leri
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from mongodb import get_users_collection, get_user_interactions_collection

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
async def get_all_users() -> List[Dict[str, Any]]:
    """Tüm kullanıcıları getir"""
    try:
        users_collection = get_users_collection()
        users = await users_collection.find().to_list(length=None)
        
        # MongoDB'nin _id alanını string'e çevir
        for user in users:
            if '_id' in user:
                user['_id'] = str(user['_id'])
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcılar getirilirken hata: {str(e)}")


@router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> Dict[str, Any]:
    """Belirli bir kullanıcıyı getir"""
    try:
        users_collection = get_users_collection()
        user = await users_collection.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail=f"Kullanıcı bulunamadı: {user_id}")
        
        if '_id' in user:
            user['_id'] = str(user['_id'])
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı getirilirken hata: {str(e)}")


@router.post("/auth/register")
async def register_user(user_data: Dict[str, Any]):
    """Yeni kullanıcı oluştur (Benzersiz email ve şifre ile)"""
    try:
        users_collection = get_users_collection()
        email = user_data.get("email")
        password = user_data.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email ve şifre zorunludur.")
        
        # Email kontrolü
        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Bu email adresi zaten kullanımda.")
            
        # Yeni user_id oluştur
        last_user = await users_collection.find_one(sort=[("user_id", -1)])
        new_id = (last_user["user_id"] + 1) if last_user else 1
        
        new_user = {
            "user_id": new_id,
            "full_name": user_data.get("full_name"),
            "email": email,
            "password": password, # Gerçek projede hash'lenmeli
            "selected_genres": user_data.get("selected_genres", [])
        }
        
        await users_collection.insert_one(new_user)
        
        # Interaction tablosuna başlangıç kaydı
        interactions_collection = get_user_interactions_collection()
        await interactions_collection.insert_one({
            "interaction_id": new_id * 1000,
            "user_id": new_id,
            "movie_id": 0,
            "is_liked": False,
            "rating": 0,
            "selected_genres": user_data.get("selected_genres", [])
        })
        
        # Şifreyi dönme
        new_user.pop("password", None)
        return {"status": "success", "user_id": new_id, "user": new_user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kayıt sırasında hata: {str(e)}")


@router.post("/auth/login")
async def login_user(login_data: Dict[str, Any]):
    """Email ve şifre ile giriş yap"""
    try:
        users_collection = get_users_collection()
        email = login_data.get("email")
        password = login_data.get("password")
        
        user = await users_collection.find_one({"email": email})
        
        if not user or user.get("password") != password:
            raise HTTPException(status_code=401, detail="Email veya şifre hatalı.")
            
        if '_id' in user:
            user['_id'] = str(user['_id'])
            
        # Şifreyi temizle
        user.pop("password", None)
        return {"status": "success", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Giriş sırasında hata: {str(e)}")


@router.post("/{user_id}/preferences")
async def save_user_preferences(user_id: int, preferences: Dict[str, Any]):
    """Kullanıcının seçtiği türleri kaydet"""
    try:
        users_collection = get_users_collection()
        interactions_collection = get_user_interactions_collection()
        selected_genres = preferences.get("selected_genres", [])
        
        # Users koleksiyonunu güncelle
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"selected_genres": selected_genres}}
        )
        
        # User_interactions koleksiyonunu güncelle
        await interactions_collection.update_many(
            {"user_id": user_id},
            {"$set": {"selected_genres": selected_genres}}
        )
            
        return {"status": "success", "message": "Tercihler kaydedildi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tercihler kaydedilirken hata: {str(e)}")
