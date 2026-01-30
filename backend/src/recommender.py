import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from mongodb import get_movies_collection, get_users_collection, get_user_interactions_collection, get_genres_collection

class CineMatchEngine:
    def __init__(self):
        self.movies_df = pd.DataFrame()
        self.cosine_sim = None
        self.count_matrix = None
        self.is_ready = False

    async def refresh_data(self):
        """Database'deki tüm filmleri çekip matematiksel modele hazırlar."""
        movies_col = get_movies_collection()
        cursor = movies_col.find({})
        movies_list = await cursor.to_list(length=None)
        self.movies_df = pd.DataFrame(movies_list)
        
        if self.movies_df.empty:
            print(" HATA: Veritabanı boş dönüyor!")
            self.is_ready = False
            return

        # MongoDB'nin karmaşık tarihini frontendin anlayacağı temiz bir yıla çeviriyoruz.
        if 'release_date' in self.movies_df.columns:
            self.movies_df['release_date'] = pd.to_datetime(self.movies_df['release_date'], errors='coerce')
            self.movies_df['year'] = self.movies_df['release_date'].dt.year.fillna(0).astype(int)
        
        # Beyni (Matematiksel Motoru) Hazırla
        self.prepare_engine()
        self.is_ready = True
        print(f" Motor Hazır: {len(self.movies_df)} film başarıyla yüklendi.")

    def prepare_engine(self):
        """Metin benzerliği ve popülerlik normalizasyonu."""
        # LLM Metadata üzerinden metin benzerliği
        self.count = CountVectorizer(stop_words='english')
        # llm_metadata boşsa boş string ile doldur
        metadata = self.movies_df['llm_metadata'].fillna('')
        self.count_matrix = self.count.fit_transform(metadata)
        self.cosine_sim = cosine_similarity(self.count_matrix)
        
        # Popülerlik verisini 0-1 arasına sıkıştır
        scaler = MinMaxScaler()
        if 'popularity' in self.movies_df.columns:
            self.movies_df['norm_popularity'] = scaler.fit_transform(self.movies_df[['popularity']].fillna(0))
        else:
            self.movies_df['norm_popularity'] = 0

    async def get_genre_names(self, genre_ids):
        """Sayısal Tür ID'lerini 'Action' gibi isimlere çevirir."""
        genres_col = get_genres_collection()
        genres = await genres_col.find({"genre_id": {"$in": genre_ids}}).to_list(length=None)
        return [g['genre_name'] for g in genres]

    async def recommend_for_guest(self, selected_genre_ids):
        """GUEST: Sadece seçtiği 1-3 tür üzerinden popüler olanları getirir."""
        if not self.is_ready:
            await self.refresh_data()
            
        genre_names = await self.get_genre_names(selected_genre_ids)
        query = "|".join(genre_names)
        
        # Seçilen türlere uyan filmleri bul
        mask = self.movies_df['llm_metadata'].str.contains(query, case=False, na=False)
        subset = self.movies_df[mask].copy()
        
        if subset.empty:
            # Türlere uyan film yoksa en popülerleri döndür
            top_indices = self.movies_df.sort_values(by='norm_popularity', ascending=False).index[:10]
            return self.format_output(top_indices)
        
        # Hibrit Skor: Tür uyumu + (Popülerlik * 0.2)
        # vote_average 0-10 arası, popülerlik 0-1 arası normalize edildi.
        subset['guest_score'] = subset['vote_average'].fillna(0) * 0.1 + subset['norm_popularity'] * 0.2
        
        top_indices = subset.sort_values(by='guest_score', ascending=False).index[:10]
        return self.format_output(top_indices)

    async def recommend_for_user(self, user_id):
        """LOGIN: Kullanıcının selected_genres + beğendiği filmlere bakar."""
        if not self.is_ready:
            await self.refresh_data()

        users_col = get_users_collection()
        user = await users_col.find_one({"user_id": user_id})
        if not user: return {"error": "Kullanıcı bulunamadı"}

        fav_genres_ids = user.get('selected_genres', [])
        interactions_col = get_user_interactions_collection()
        interactions = await interactions_col.find({"user_id": user_id, "is_liked": True}).to_list(length=None)

        if not fav_genres_ids and not interactions:
            # En popüler 10 filmi getir
            top_indices = self.movies_df.sort_values(by='norm_popularity', ascending=False).index[:10]
            return self.format_output(top_indices)

        # 1. Kayıt olurken seçtiği türler
        fav_genres = await self.get_genre_names(fav_genres_ids)
        
        # Benzerlik puanlarını toplayacağımız havuz
        final_scores = np.zeros(len(self.movies_df))
        
        # Beğendiği her film için tüm kütüphane ile benzerlik puanı ekle
        for interact in interactions:
            m_id = interact['movie_id']
            rating_weight = interact.get('rating', 3) / 5.0
            try:
                # movieId veya id kontrolü
                idx_list = self.movies_df[self.movies_df['movieId'] == m_id].index
                if idx_list.empty:
                    idx_list = self.movies_df[self.movies_df['id'] == m_id].index
                
                if not idx_list.empty:
                    idx = idx_list[0]
                    final_scores += self.cosine_sim[idx] * rating_weight
            except Exception as e:
                print(f"Benzerlik hesaplama hatası (movie_id: {m_id}): {e}")
                continue

        # Tür Bonusu
        genre_mask = np.zeros(len(self.movies_df))
        if fav_genres:
            genre_query = "|".join(fav_genres)
            genre_mask = self.movies_df['llm_metadata'].str.contains(genre_query, case=False, na=False).astype(int).values
        
        # FINAL MATEMATİKSEL FORMÜL: Benzerlik (%50) + Tür Uyumu (%30) + Popülerlik (%20)
        total_scores = (final_scores * 0.5) + (genre_mask * 0.3) + (self.movies_df['norm_popularity'] * 0.2)
        
        # En iyi 10 filmi seç
        top_indices = np.argsort(total_scores)[::-1][:10]
        return self.format_output(top_indices)

    def format_output(self, indices):
        """Frontend'e temiz veri döner."""
        results = []
        for idx in indices:
            row = self.movies_df.iloc[idx]
            results.append({
                "movieId": int(row['movieId']) if 'movieId' in row and pd.notnull(row['movieId']) else int(row['id']) if 'id' in row and pd.notnull(row['id']) else 0,
                "title": row['title'],
                "original_language": row.get('original_language', 'en'),
                "vote_average": float(row['vote_average']) if pd.notnull(row['vote_average']) else 0.0,
                "release_date": str(row['release_date']) if pd.notnull(row['release_date']) else "",
                "poster_url": row.get('poster_url', ''),
                "llm_metadata": row.get('llm_metadata', '')
            })
        return results

# Singleton instance
engine = CineMatchEngine()
