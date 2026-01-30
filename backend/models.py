"""
Pydantic modelleri - API request/response validasyonu için
"""
from pydantic import BaseModel, Field
from typing import Optional, Any


class User(BaseModel):
    """Kullanıcı modeli"""
    user_id: int
    full_name: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "full_name": "Batuhan Bilgili",
                "email": "batuhan@example.com"
            }
        }


class UserInteraction(BaseModel):
    """Kullanıcı etkileşim modeli"""
    interaction_id: int
    user_id: int
    movie_id: int
    is_liked: bool
    rating: int = Field(..., ge=1, le=5)

    class Config:
        json_schema_extra = {
            "example": {
                "interaction_id": 1001,
                "user_id": 1,
                "movie_id": 5,
                "is_liked": True,
                "rating": 5
            }
        }


class Genre(BaseModel):
    """Tür modeli"""
    genre_id: int
    genre_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "genre_id": 1,
                "genre_name": "Action"
            }
        }


class MovieGenre(BaseModel):
    """Film-tür ilişki modeli"""
    movie_id: int
    genre_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": 1,
                "genre_id": 2
            }
        }


class Movie(BaseModel):
    """Film modeli"""
    movieId: int
    title: str
    imdbId: Optional[int] = None
    tmdbId: Optional[int] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    popularity: Optional[float] = None
    release_date: Optional[Any] = None
    runtime: Optional[int] = None
    vote_average: Optional[float] = None
    poster_url: Optional[str] = None
    llm_metadata: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "imdbId": 114709,
                "tmdbId": 862,
                "avg_rating": 3.8974375697494095,
                "rating_count": 68997,
                "original_language": "en",
                "original_title": "Toy Story",
                "popularity": 20.925,
                "release_date": "1995-11-22T00:00:00.000Z",
                "runtime": 81,
                "vote_average": 7.97,
                "poster_url": "https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
                "llm_metadata": "Film: Toy Story (1995), Türler: Adventure, Animation, Children, Comedy"
            }
        }
