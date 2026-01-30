"""
Tür (Genre) API endpoint'leri
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from mongodb import get_genres_collection, get_movie_genres_collection

router = APIRouter(prefix="/api/genres", tags=["genres"])


@router.get("")
async def get_all_genres() -> List[Dict[str, Any]]:
    """Tüm türleri getir"""
    try:
        genres_collection = get_genres_collection()
        genres = await genres_collection.find().to_list(length=None)
        
        for genre in genres:
            if '_id' in genre:
                genre['_id'] = str(genre['_id'])
        
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Türler getirilirken hata: {str(e)}")


@router.get("/movie/{movie_id}")
async def get_movie_genres(movie_id: int) -> List[Dict[str, Any]]:
    """Belirli bir filmin türlerini getir"""
    try:
        # Önce film-tür ilişkilerini al
        movie_genres_collection = get_movie_genres_collection()
        movie_genre_relations = await movie_genres_collection.find({"movie_id": movie_id}).to_list(length=None)
        
        if not movie_genre_relations:
            return []
        
        # Tür ID'lerini topla
        genre_ids = [relation["genre_id"] for relation in movie_genre_relations]
        
        # Türleri getir
        genres_collection = get_genres_collection()
        genres = await genres_collection.find({"genre_id": {"$in": genre_ids}}).to_list(length=None)
        
        for genre in genres:
            if '_id' in genre:
                genre['_id'] = str(genre['_id'])
        
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Film türleri getirilirken hata: {str(e)}")
