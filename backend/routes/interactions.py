"""
Kullanıcı etkileşim API endpoint'leri
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from mongodb import get_user_interactions_collection

router = APIRouter(prefix="/api/interactions", tags=["interactions"])


@router.get("")
async def get_all_interactions() -> List[Dict[str, Any]]:
    """Tüm etkileşimleri getir"""
    try:
        interactions_collection = get_user_interactions_collection()
        interactions = await interactions_collection.find().to_list(length=None)
        
        for interaction in interactions:
            if '_id' in interaction:
                interaction['_id'] = str(interaction['_id'])
        
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Etkileşimler getirilirken hata: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_interactions(user_id: int) -> List[Dict[str, Any]]:
    """Belirli bir kullanıcının etkileşimlerini getir"""
    try:
        interactions_collection = get_user_interactions_collection()
        interactions = await interactions_collection.find({"user_id": user_id}).to_list(length=None)
        
        for interaction in interactions:
            if '_id' in interaction:
                interaction['_id'] = str(interaction['_id'])
        
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı etkileşimleri getirilirken hata: {str(e)}")


@router.post("")
async def create_interaction(data: Dict[str, Any]):
    """Yeni bir etkileşim kaydet veya güncelle"""
    try:
        interactions_collection = get_user_interactions_collection()
        user_id = data.get("user_id")
        movie_id = data.get("movie_id")
        
        # Varsa güncelle, yoksa oluştur
        existing = await interactions_collection.find_one({"user_id": user_id, "movie_id": movie_id})
        
        if existing:
            await interactions_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "is_liked": data.get("is_liked", existing.get("is_liked")),
                    "rating": data.get("rating", existing.get("rating"))
                }}
            )
            return {"status": "updated"}
        else:
            # Yeni interaction_id oluştur
            last_interaction = await interactions_collection.find_one(sort=[("interaction_id", -1)])
            new_id = (last_interaction["interaction_id"] + 1) if last_interaction else 1001
            
            # Kullanıcın tercihlerini alalım
            from mongodb import get_users_collection
            users_collection = get_users_collection()
            user = await users_collection.find_one({"user_id": user_id})
            selected_genres = user.get("selected_genres", []) if user else []

            new_interaction = {
                "interaction_id": new_id,
                "user_id": user_id,
                "movie_id": movie_id,
                "is_liked": data.get("is_liked", False),
                "rating": data.get("rating", 0),
                "selected_genres": selected_genres
            }
            await interactions_collection.insert_one(new_interaction)
            return {"status": "created", "interaction_id": new_id}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Etkileşim kaydedilirken hata: {str(e)}")


@router.delete("/user/{user_id}/movie/{movie_id}")
async def delete_interaction(user_id: int, movie_id: int):
    """Etkileşimi sil (Listeden çıkarma işlemi için)"""
    try:
        interactions_collection = get_user_interactions_collection()
        result = await interactions_collection.delete_many({"user_id": user_id, "movie_id": movie_id})
        return {"status": "deleted", "count": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Etkileşim silinirken hata: {str(e)}")
