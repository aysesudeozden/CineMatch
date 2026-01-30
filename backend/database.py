import json
import os
import csv

# --- YAPILANDIRMA VE DOSYA YOLLARI ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "users.json")
MOVIES_CSV_PATH = os.path.join(BASE_DIR, "data", "movies.csv")

def load_users():
    """users.json veritabanını yükler. Hata durumunda boş liste döner."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        return []

def save_users(users_list):
    """Kullanıcı verilerini users.json dosyasına kalıcı olarak kaydeder."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as file:
        json.dump(users_list, file, indent=4, ensure_ascii=False)

def get_valid_movie_titles():
    """movies.csv dosyasındaki geçerli film isimlerini kontrol için çeker."""
    titles = []
    if not os.path.exists(MOVIES_CSV_PATH):
        return None  # CSV henüz hazır değilse kontrolü atlar
    
    with open(MOVIES_CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            titles.append(row['title'].lower())
    return titles

def add_user(name, liked_genres):
    """Yeni kullanıcı profili oluşturur ve kaydeder."""
    users = load_users()
    new_user = {
        "user_id": len(users) + 1,
        "name": name,
        "liked_genres": liked_genres,
        "watched_movies": []
    }
    users.append(new_user)
    save_users(users)
    print(f"\n[SİSTEM]: '{name}' başarıyla kaydedildi. ID: {new_user['user_id']}")

def add_movie_rating(user_id, movie_title, rating):
    """Filmi doğrular ve kullanıcının izleme geçmişine puanıyla ekler."""
    valid_movies = get_valid_movie_titles()
    
    if valid_movies is not None and movie_title.lower() not in valid_movies:
        print(f"[HATA]: '{movie_title}' film listesinde bulunamadı!")
        return

    users = load_users()
    for user in users:
        if user["user_id"] == user_id:
            movie_exists = False
            for movie in user["watched_movies"]:
                if movie["title"].lower() == movie_title.lower():
                    movie["rating"] = rating
                    movie_exists = True
                    break
            
            if not movie_exists:
                user["watched_movies"].append({"title": movie_title, "rating": rating})
            save_users(users)
            print(f"[SİSTEM]: {movie_title} için {rating} puanı kaydedildi.")
            return
    print(f"[HATA]: ID {user_id} bulunamadı.")

def get_trending_movies():
    """Tüm kullanıcıların puanlarını analiz ederek popüler filmleri listeler."""
    users = load_users()
    movie_stats = {} # {film_adı: [puanlar]}
    
    for user in users:
        for movie in user["watched_movies"]:
            title = movie["title"]
            rating = movie["rating"]
            if title not in movie_stats:
                movie_stats[title] = []
            movie_stats[title].append(rating)
    
    # Ortalama puanı hesapla ve sırala
    trending = []
    for title, ratings in movie_stats.items():
        avg = sum(ratings) / len(ratings)
        trending.append({"title": title, "avg_rating": avg, "votes": len(ratings)})
    
    return sorted(trending, key=lambda x: (x['avg_rating'], x['votes']), reverse=True)

# --- YÖNETİM PANELİ ---
if __name__ == "__main__":
    while True:
        print("\n=== CineMatch-AI Backend Kontrol Paneli ===")
        print("1. Yeni Kullanıcı Ekle")
        print("2. Filme Puan Ver")
        print("3. Kullanıcıları Listele")
        print("4. Trend Filmleri Gör (Görev 7)")
        print("5. Çıkış")
        
        choice = input("\nSeçiminiz: ")
        
        if choice == "1":
            name = input("İsim: ")
            genres = [g.strip() for g in input("Türler (virgülle): ").split(",")]
            add_user(name, genres)
        elif choice == "2":
            try:
                uid = int(input("Kullanıcı ID: "))
                title = input("Film Adı: ")
                rate = float(input("Puan (0-10): "))
                add_movie_rating(uid, title, rate)
            except ValueError: print("Hatalı giriş!")
        elif choice == "3":
            for u in load_users():
                print(f"ID: {u['user_id']} | {u['name']} | İzlediği: {len(u['watched_movies'])}")
        elif choice == "4":
            trends = get_trending_movies()
            print("\n--- TREND LİSTESİ ---")
            for m in trends[:5]:
                print(f"{m['title']} - Puan: {m['avg_rating']:.1f} ({m['votes']} oy)")
        elif choice == "5":
            break
