#! Adal'ın Algoritması - Versiyon 4.0 (FINAL: MongoDB, Login/Guest Ayrımı & Hibrit Model)
# Bu kod artık .csv dosyalarına veda eder, kalbi tamamen MongoDB ile canlı atar!

import os # OS emekti, OS Operating System'di. .env içindeki gizli MONGO_URL'i okumamızı sağlar.
import pandas as pd # Verileri tablo (DataFrame) haline getirip üzerinde fink atmamızı sağlar.
import numpy as np # Matematiksel ağırlıklandırma ve benzerlik puanları için beynimiz.
from flask import Flask, request, jsonify # Sude'nin (Frontend) kapımızı çalması için kurduğumuz API köprüsü.
from flask_cors import CORS # Sude ile aramızdaki güvenlik engelini (CORS) ortadan kaldırır.
from pymongo import MongoClient # MongoDB bulutuna bağlanan elçimiz.
from dotenv import load_dotenv # .env içindeki hassas bilgileri (API Key gibi) içeri alır.
from sklearn.feature_extraction.text import CountVectorizer # Kelimeleri bilgisayarın anlayacağı sayılara çevirir.
from sklearn.metrics.pairwise import cosine_similarity # Filmler arası benzerliği matematiksel ölçer.
from sklearn.preprocessing import MinMaxScaler # Popülerlik gibi uçuk sayıları 0-1 arasına hapseder.

# --- 1. AYARLAR VE BAĞLANTI ---
load_dotenv() # .env dosyasını hafızaya yükle.
app = Flask(__name__)
CORS(app) # Sude'nin frontend'i bizimle sorunsuz konuşsun diye izin veriyoruz.

# MONGO_URL'in .env içinde MONGO_URL olarak saklanmalı.
MONGO_URL = os.getenv("MONGO_URL")

class CineMatchEngine:
    def __init__(self):
        # MongoDB'ye bağlanıyoruz (Anahtarı kilide taktık).
        self.client = MongoClient(MONGO_URL)
        # Veritabanı ismimiz: CineMatch_db
        self.db = self.client['CineMatch_db'] 
        
        # Tablolarımızı (Collections) tek tek tanımlıyoruz.
        self.movies_col = self.db['movies']
        self.users_col = self.db['users']
        self.interactions_col = self.db['user_interactions']
        self.genres_col = self.db['genres']
        
        # Verileri bir kez çekip hafızada modellemek hız kazandırır.
        self.refresh_data()

    def refresh_data(self):
        """Database'deki tüm filmleri çekip matematiksel modele hazırlar."""
        cursor = self.movies_col.find({})
        self.movies_df = pd.DataFrame(list(cursor))
        
        if self.movies_df.empty:
            print("❌ HATA: Veritabanı boş dönüyor!")
            return

        # MongoDB'nin karmaşık tarihini frontendin anlayacağı temiz bir yıla çeviriyoruz.
        if 'release_date' in self.movies_df.columns:
            self.movies_df['release_date'] = pd.to_datetime(self.movies_df['release_date'], errors='coerce')
            self.movies_df['year'] = self.movies_df['release_date'].dt.year.fillna(0).astype(int)
        
        # Beyni (Matematiksel Motoru) Hazırla
        self.prepare_engine()
        print(f"✅ Motor Hazır: {len(self.movies_df)} film başarıyla yüklendi.")

    def prepare_engine(self):
        """v3'ten gelen o meşhur kelime sayıcı ve benzerlik matrisi burası."""
        # LLM Metadata üzerinden metin benzerliği (v3 Mirası)
        self.count = CountVectorizer(stop_words='english')
        self.count_matrix = self.count.fit_transform(self.movies_df['llm_metadata'].fillna(''))
        self.cosine_sim = cosine_similarity(self.count_matrix)
        
        # Popülerlik verisini 0-1 arasına sıkıştır (v3 Mirası)
        scaler = MinMaxScaler()
        self.movies_df['norm_popularity'] = scaler.fit_transform(self.movies_df[['popularity']].fillna(0))

    def get_genre_names(self, genre_ids):
        """Sayısal Tür ID'lerini (Örn: 2) 'Action' gibi isimlere çevirir."""
        genres = list(self.genres_col.find({"genre_id": {"$in": genre_ids}}))
        return [g['genre_name'] for g in genres]

    # --- LOGIN / GUEST AYRIMI ---
    
    def recommend_for_guest(self, selected_genre_ids):
        """GUEST: Sadece seçtiği 1-3 tür üzerinden popüler olanları getirir."""
        genre_names = self.get_genre_names(selected_genre_ids)
        query = "|".join(genre_names) # Türleri yan yana diziyoruz (Örn: Action|Comedy)
        
        # Seçilen türlere uyan filmleri bul
        mask = self.movies_df['llm_metadata'].str.contains(query, case=False, na=False)
        subset = self.movies_df[mask].copy()
        
        # Hibrit Skor: Tür uyumu + (Popülerlik * 0.2)
        subset['guest_score'] = subset['vote_average'] * 0.1 + subset['norm_popularity'] * 0.2
        
        top_indices = subset.sort_values(by='guest_score', ascending=False).index[:10]
        return self.format_output(top_indices)

    def recommend_for_user(self, user_id):
        """LOGIN: Kullanıcının selected_genres + beğendiği filmlere (is_liked) bakar."""
        user = self.users_col.find_one({"user_id": user_id})
        if not user: return {"error": "Kullanıcı bulunamadı"}

        # EMNİYET KEMERİ: Eğer kullanıcı tamamen boşsa, ona popülerleri fırlat
        fav_genres_ids = user.get('selected_genres', [])
        interactions = list(self.interactions_col.find({"user_id": user_id, "is_liked": True}))

        if not fav_genres_ids and not interactions:
            print(f"ℹ️ User {user_id} tertemiz, popüler filmler gönderiliyor.")
            # En popüler 10 filmi getir
            top_indices = self.movies_df.sort_values(by='norm_popularity', ascending=False).index[:10]
            return self.format_output(top_indices)

        # 1. Kayıt olurken seçtiği türler (selected_genres)
        fav_genres = self.get_genre_names(user.get('selected_genres', []))
        
        # 2. Daha önce beğendiği filmler (interactions tablosu)
        interactions = list(self.interactions_col.find({"user_id": user_id, "is_liked": True}))
        liked_movie_ids = [i['movie_id'] for i in interactions]

        # Benzerlik puanlarını toplayacağımız boş bir havuz oluştur
        final_scores = np.zeros(len(self.movies_df))
        
        # Beğendiği her film için tüm kütüphane ile benzerlik puanı ekle (Rating ağırlıklı)
        for interact in interactions:
            m_id = interact['movie_id']
            rating_weight = interact.get('rating', 3) / 5.0 # 5 puan verdiyse etkisi büyük olur!
            try:
                idx = self.movies_df[self.movies_df['movieId'] == m_id].index[0]
                final_scores += self.cosine_sim[idx] * rating_weight
            except: continue

        # Tür Bonusu: Girişte seçtiği türler için ek puan
        genre_query = "|".join(fav_genres)
        genre_mask = self.movies_df['llm_metadata'].str.contains(genre_query, case=False, na=False).astype(int)
        
        # FINAL MATEMATİKSEL FORMÜL: Benzerlik (%50) + Tür Uyumu (%30) + Popülerlik (%20)
        total_scores = (final_scores * 0.5) + (genre_mask * 0.3) + (self.movies_df['norm_popularity'] * 0.2)
        
        # En iyi 10 filmi seç
        top_indices = np.argsort(total_scores)[::-1][:10]
        return self.format_output(top_indices)

    def format_output(self, indices):
        """Sude'nin (Frontend) ekranda basması için tertemiz bir liste hazırlar."""
        results = []
        for idx in indices:
            row = self.movies_df.iloc[idx]
            results.append({
                "title": row['title'],
                "original_language": row['original_language'],
                "vote_average": row['vote_average'],
                "release_date": str(row['release_date']),
                "poster_url": row['poster_url']
            })
        return results

# --- 2. ÇALIŞTIRMA VE API ---
engine = CineMatchEngine()

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_id = data.get('user_id')
    selected_genres = data.get('selected_genres', []) # Guest için [7, 16, 15]

    if user_id:
        # Kayıtlı kullanıcı algoritmasını ateşle!
        return jsonify(engine.recommend_for_user(user_id))
    else:
        # Misafir kullanıcı algoritmasını ateşle!
        return jsonify(engine.recommend_for_guest(selected_genres))

if __name__ == '__main__':
    # host='0.0.0.0' önemli, Sude kendi bilgisayarından bu IP ile sana ulaşacak.
    app.run(debug=True, host='0.0.0.0', port=5000)