# Türk Telekom Kurumsal RAG Chatbot

Kurumsal dokümanlar üzerinde RAG (Retrieval-Augmented Generation) tabanlı, güvenli ve özelleştirilebilir bir soru-cevap asistanı.

## Özellikler

- **Admin Paneli:** Sadece admin anahtarı ile prompt (asistan kimliği ve kuralları) düzenlenebilir.
- **Güvenli Giriş:** Admin girişi yapılmadan prompt düzenleme ve yönetim mümkün değildir.
- **Session Tabanlı Yetki:** Admin girişi her oturumda tekrar istenir, güvenlik üst düzeydedir.
- **Modern Arayüz:** Şık, responsive ve kullanıcı dostu frontend.
- **Hafıza Temizleme:** Sohbet geçmişini admin olarak sıfırlayabilirsiniz.
- **Kaynak Gösterimi:** Yanıtlarda kullanılan dokümanlar ve kaynaklar listelenir.
- **Kolay Kurulum:** Tüm bağımlılıklar requirements.txt ile yönetilir.

## Kurulum

1. **Depoyu Klonlayın:**
   ```bash
   git clone <repo-url>
   cd WEB_CHATBOT
   ```
2. **Python Ortamı Oluşturun:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # veya
   source venv/bin/activate  # Linux/Mac
   ```
3. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```
4. **.env Dosyasını Düzenleyin:**
   ```env
   ADMIN_API_KEY=buraya_güçlü_bir_anahtar
   ```
5. **Veri Tabanını Oluşturun:**
   ```bash
   python ingest.py
   ```
6. **Uygulamayı Başlatın:**
   ```bash
   python main.py
   ```
7. **Web Arayüzüne Erişin:**
   - Tarayıcıdan `http://localhost:8000` adresine gidin.

## Kullanım

- **Admin Girişi:** Sağ üstteki "🔑 Admin Girişi" butonuna tıklayın ve .env dosyasındaki admin anahtarını girin.
- **Prompt Düzenleme:** Giriş yaptıktan sonra ⚙️ simgesiyle promptu güncelleyebilirsiniz.
- **Çıkış:** "🚪 Çıkış Yap" ile admin oturumunu sonlandırabilirsiniz.
- **Sohbet:** Ana ekrandan asistan ile Türk Telekom kurumsal hizmetleri hakkında sohbet edebilirsiniz.

## Dosya Yapısı

```
WEB_CHATBOT/
├── main.py           # FastAPI sunucu ve API
├── ingest.py         # Dokümanları vektör veritabanına ekler
├── system.py         # Chatbot iş mantığı
├── requirements.txt  # Gerekli Python paketleri
├── .env              # Ortam değişkenleri (admin anahtarı)
├── prompt.txt        # Düzenlenebilir asistan promptu
├── static/
│   └── index.html    # Modern frontend arayüzü
├── data/             # Dokümanlarınız
└── vector_db/        # Vektör veritabanı (Chroma)
```

## Güvenlik
- Admin anahtarı tarayıcıda sessionStorage ile tutulur, sayfa kapatılınca silinir.
- Prompt ve yönetim endpointleri sadece admin anahtarı ile erişilebilir.
- .env dosyanızı ve admin anahtarınızı kimseyle paylaşmayın!
