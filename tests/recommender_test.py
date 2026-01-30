import requests
import json

URL = "http://localhost:5000/recommend"

def test_et(mesaj, payload):
    print(f"\n--- 🔍 {mesaj} ---")
    try:
        response = requests.post(URL, json=payload)
        print(json.dumps(response.json()[:2], indent=2, ensure_ascii=False)) # İlk 2 filmi görsek yeter
        print(f"✅ Toplam {len(response.json())} film geldi.")
    except Exception as e:
        print(f"❌ Hata: {e}")

# TEST 1: Normal Misafir
test_et("MİSAFİR (Normal Tür Seçimi)", {"selected_genres": [1, 2, 16]})

# TEST 2: Boş Misafir (Cold Start Testi)
test_et("MİSAFİR (Hiçbir Tür Seçmedi - Emniyet Kemeri Testi)", {"selected_genres": []})

# TEST 3: Kayıtlı Kullanıcı
test_et("LOGIN (Batuhan)", {"user_id": 1})