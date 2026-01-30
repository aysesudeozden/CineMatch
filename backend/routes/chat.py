"""
Chat API endpoint'leri - CineMatch AI Engine Entegrasyonu
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from openai import AsyncOpenAI
from mongodb import get_database
from pathlib import Path
from dotenv import load_dotenv

# Root .env dosyasını bul ve yükle
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class CineMatchEngine:
    def __init__(self):
        # OpenAI API Key .env'den alınır
        api_key = os.getenv("OPENAI_API_KEY")
        # Asenkron client kullan
        self.client = AsyncOpenAI(api_key=api_key)

    async def get_personalized_recommendation(self, user_id: int, user_message: str):
        # Database nesnesini her seferinde güncel al
        db = get_database()
        if db is None:
            return "Veritabanı bağlantısı henüz kurulmadı. Lütfen biraz bekleyin."

        try:
            # 1. Kullanıcıyı ve Tercihlerini Çek
            user = await db.users.find_one({"user_id": user_id})
            if not user:
                return "Kullanıcı profiliniz veritabanında bulunamadı."

            # Etkileşim geçmişi ve türler
            interactions_cursor = db.user_interactions.find({"user_id": user_id})
            interactions = await interactions_cursor.to_list(length=100)
            
            genres_cursor = db.genres.find()
            genres_list = await genres_cursor.to_list(length=100)
            genre_map = {g['genre_id']: g['genre_name'] for g in genres_list}

            # Kullanıcının seçtiği tür isimlerini belirle
            fav_genre_names = [genre_map.get(gid) for gid in user.get('selected_genres', []) if genre_map.get(gid)]
            
            # 2. Etkileşim Geçmişinden Özet Çıkar
            liked_movies_metadata = []
            disliked_ids = []
            
            for inter in interactions:
                movie = await db.movies.find_one({"movieId": inter['movie_id']})
                if movie:
                    # 'Listem'e eklediği her şeyi bir beğeni/ilgi sinyali olarak kabul et
                    if inter.get('is_liked'):
                        liked_movies_metadata.append(movie.get('llm_metadata', movie.get('title')))
                    elif inter.get('is_liked') is False:
                        disliked_ids.append(inter['movie_id'])

            # 3. Aday Havuzu Oluştur
            watched_ids = [i['movie_id'] for i in interactions]
            exclude_ids = list(set(watched_ids + disliked_ids))
            
            query = {
                "movieId": {"$nin": exclude_ids},
                "vote_average": {"$gt": 6.0}
            }
            
            candidates_cursor = db.movies.find(query).sort("popularity", -1).limit(15)
            candidates = await candidates_cursor.to_list(length=15)
            candidate_context = "\n".join([c.get('llm_metadata', c.get('title', '')) for c in candidates])

            # 4. LLM Promptu
            system_prompt = f"""
            Sen CineMatch film uzmanısın. Kullanıcının zevkini analiz ederek ona en iyi tavsiyeleri verirsin.
            
            KULLANICI VERİLERİ (Hiyerarşik Öncelik):
            1. KULLANICININ MEVCUT LİSTESİ ("Listem" - En Önemli): {liked_movies_metadata[:10]}
            2. Kayıtta seçtiği genel favori türler: {fav_genre_names}
            
            GÖREV VE ÖNCELİK KURALLARI:
            - BİRİNCİL ÖNCELİK "LİSTEM": Kullanıcının zevkini belirleyen ana unsur "Listem"deki filmlerdir. Türler sadece ek bilgidir.
            - LİSTEDEN SEÇİM TALEBİ: Eğer kullanıcı "Listemden film seç", "Listemden ne izleyeyim?" gibi kendi listesiyle ilgili bir şey sorarsa, ADAY LİSTESİ'ni DEĞİL, yukarıdaki "KULLANICININ MEVCUT LİSTESİ" içerisinden seçim yap ve nedenini açıkla.
            - YENİ ÖNERİ TALEBİ: Eğer kullanıcı genel bir öneri isterse, "ADAY LİSTESİ"nden seçim yap. Bu seçimi yaparken mutlaka "Listem"deki filmlerle benzerlik kur. (Örn: "Listendeki **Inception** gibi akıl oyunlarını sevdiğin için aday listesinden şu filmi seçtim...")
            
            KESİN KURALLAR:
            1. Yeni öneri verirken sadece aşağıda verilen "ADAY LİSTESİ" içerisindeki filmleri kullan. Dışarıdan film uydurma.
            2. Film isimlerini mutlaka **Kalın Yazı** formatında kullan.
            3. Cevaplarını paragraflar halinde yaz, her öneri arasında boşluk bırak.
            
            ADAY LİSTESİ:
            {candidate_context}
            
            Cevabını Türkçe, samimi ve uzman bir dille ver.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Öneri motoru işlem sırasında bir hata aldı: {str(e)}"

# Engine instance
engine = CineMatchEngine()

@router.post("")
async def chat_with_ai(request: ChatRequest):
    """CineMatch AI Engine ile kişiselleştirilmiş yanıt döndür"""
    # Debug için payload kontrolü yapalım (Opsiyonel)
    if request.user_id is None:
        raise HTTPException(status_code=401, detail="Chatbotu kullanmak için giriş yapmalısınız.")
        
    try:
        response = await engine.get_personalized_recommendation(request.user_id, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")
