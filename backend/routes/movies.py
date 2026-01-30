"""
Film API endpoint'leri
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from mongodb import get_movies_collection

router = APIRouter(prefix="/api/movies", tags=["movies"])


@router.get("")
async def get_all_movies(
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(20, ge=1, le=100, description="Getirilecek kayıt sayısı"),
    search: Optional[str] = Query(None, description="Film adında arama"),
    genre_ids: Optional[str] = Query(None, description="Virgülle ayrılmış tür ID'leri"),
    sort_by: Optional[str] = Query(None, description="Sıralama kriteri (popularity gibi)")
) -> List[Dict[str, Any]]:

    """Tüm filmleri getir (pagination ve tür filtresi ile)"""
    try:
        movies_collection = get_movies_collection()
        
        # Temel arama filtresi
        query = {}
        if search:
            query["title"] = {"$regex": search, "$options": "i"}
            
        # Tür filtresi ekle
        if genre_ids:
            genre_id_list = [int(gid.strip()) for gid in genre_ids.split(",") if gid.strip().isdigit()]
            if genre_id_list:
                # movie_genres koleksiyonundan bu türlere sahip film ID'lerini al
                from mongodb import get_movie_genres_collection
                mg_collection = get_movie_genres_collection()
                
                # Belirtilen türlerden HERHANGİ BİRİNE sahip filmleri bul
                relations = await mg_collection.find({"genre_id": {"$in": genre_id_list}}).to_list(length=None)
                movie_ids = list(set([rel["movie_id"] for rel in relations]))
                
                # Film sorgusuna bu ID'leri ekle
                if movie_ids:
                    query["$and"] = query.get("$and", []) + [{"movieId": {"$in": movie_ids}}]
                else:
                    # Tür seçilmiş ama film bulunamamışsa boş liste dön
                    return []
        
        # Filmleri getir
        cursor = movies_collection.find(query).skip(skip).limit(limit)
        
        if sort_by == "popularity":
            cursor = cursor.sort("popularity", -1)
            
        movies = await cursor.to_list(length=limit)
        
        # MongoDB'nin _id alanını string'e çevir
        for movie in movies:
            if '_id' in movie:
                movie['_id'] = str(movie['_id'])
        
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filmler getirilirken hata: {str(e)}")



@router.get("/{movie_id}")
async def get_movie_by_id(movie_id: int) -> Dict[str, Any]:
    """Belirli bir filmi getir"""
    try:
        movies_collection = get_movies_collection()
        # Hem movieId hem de id olarak aramayı dene
        movie = await movies_collection.find_one({"$or": [{"movieId": movie_id}, {"id": movie_id}]})
        
        if not movie:
            raise HTTPException(status_code=404, detail=f"Film bulunamadı: {movie_id}")
        
        if '_id' in movie:
            movie['_id'] = str(movie['_id'])
        return movie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Film getirilirken hata: {str(e)}")


@router.get("/search/query")
async def search_movies(q: str = Query(..., min_length=1, description="Arama terimi")) -> List[Dict[str, Any]]:
    """Film ara"""
    try:
        movies_collection = get_movies_collection()
        
        # Başlık veya orijinal başlıkta ara
        query = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"original_title": {"$regex": q, "$options": "i"}}
            ]
        }
        
        movies = await movies_collection.find(query).limit(50).to_list(length=50)
        
        for movie in movies:
            if '_id' in movie:
                movie['_id'] = str(movie['_id'])
        
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arama yapılırken hata: {str(e)}")
