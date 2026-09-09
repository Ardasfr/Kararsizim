# 🤔 Kararsızım — Proje Planı ve Geliştirici Rehberi

> **Hedef:** Kullanıcıların kararsız kaldıkları konularda hızlıca anket oluşturup topluluktan görüş alabildiği, sade ve eğlenceli bir web platformu.

---

## 📋 İçindekiler

1. [Proje Özeti](#proje-özeti)
2. [Teknik Yığın](#teknik-yığın)
3. [Mimari ve Klasör Yapısı](#mimari-ve-klasör-yapısı)
4. [Veritabanı Şeması](#veritabanı-şeması)
5. [URL ve Sayfa Haritası](#url-ve-sayfa-haritası)
6. [Özellik Listesi](#özellik-listesi)
7. [Arayüz Rehberi](#arayüz-rehberi)
8. [Faz Planı](#faz-planı)
9. [Ortam Değişkenleri](#ortam-değişkenleri)
10. [Deployment (Vercel)](#deployment-vercel)

---

## Proje Özeti

**"Kararsızım"**, kullanıcıların günlük kararlarını toplulukla paylaşıp hızlıca anket yapabildiği minimalist bir oylamalı karar platformudur.

### Temel Kurallar

| Kural | Detay |
|---|---|
| Anket seçenekleri | En az 2, en fazla 5 |
| Üyelik gerekliliği | Sadece anket **oluşturmak** için |
| Oy verme | Üye olmadan da mümkün (anonim) |
| Anket görüntüleme | Herkes görebilir |
| Takip / arkadaş sistemi | **Yok** — herkese açık feed |
| Kullanıcı adı | Anketlerde görünür, e-posta **gizlenir** |

---

## Teknik Yığın

| Katman | Teknoloji |
|---|---|
| Backend | Python 3.11+, Django 5.x |
| Veritabanı | Supabase (PostgreSQL) |
| Frontend | HTML, CSS, Vanilla JavaScript (Django template engine) |
| Deployment | Vercel (Serverless — `vercel-python` runtime) |
| Kimlik Doğrulama | Django'nun yerleşik `django.contrib.auth` sistemi |
| Statik Dosyalar | WhiteNoise (lokal) / Vercel CDN (prod) |
| Ortam Yönetimi | `python-dotenv` |

> **Not:** Ayrı bir frontend framework (React, Vue vb.) kullanılmayacak. Her şey tek repoda, Django template'leri üzerinden yönetilecek.

---

## Mimari ve Klasör Yapısı

```
kararsizim/
├── kararsizim/               # Django proje ayarları
│   ├── settings/
│   │   ├── base.py           # Ortak ayarlar
│   │   ├── development.py    # Lokal geliştirme
│   │   └── production.py     # Vercel / Supabase
│   ├── urls.py
│   └── wsgi.py
│
├── polls/                    # Ana uygulama (anketler)
│   ├── models.py             # Poll, Choice, Vote modelleri
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templatetags/
│       └── poll_extras.py    # Yüzde hesaplama gibi template filter'lar
│
├── accounts/                 # Kullanıcı yönetimi
│   ├── models.py             # CustomUser modeli
│   ├── views.py
│   ├── urls.py
│   └── forms.py
│
├── templates/                # Tüm HTML şablonları
│   ├── base.html             # Ana layout
│   ├── partials/
│   │   ├── _navbar.html
│   │   └── _poll_card.html   # Tekrar kullanılan anket kartı
│   ├── polls/
│   │   ├── index.html        # Ana sayfa (anket feed)
│   │   ├── detail.html       # Anket detay + oy
│   │   └── create.html       # Anket oluşturma formu
│   └── accounts/
│       ├── login.html
│       ├── register.html
│       └── profile.html
│
├── static/
│   ├── css/
│   │   └── style.css         # Global stiller + CSS değişkenleri
│   ├── js/
│   │   └── main.js           # Dinamik seçenek ekleme, oy animasyonları
│   └── img/
│       └── logo.svg
│
├── requirements.txt
├── vercel.json               # Vercel yapılandırması
├── build_files.sh            # Vercel build betiği
├── .env.example              # Ortam değişkeni şablonu
└── manage.py
```

---

## Veritabanı Şeması

### `accounts_customuser`

```
id            UUID / BigInt  PK
username      VARCHAR(30)    UNIQUE, NOT NULL
email         VARCHAR(255)   UNIQUE, NOT NULL
password      VARCHAR        (hashed)
date_joined   TIMESTAMP
is_active     BOOLEAN
```

### `polls_poll`

```
id            UUID           PK
author        FK → CustomUser (NULL = anonim; ama biz zorunlu yapıyoruz)
question      VARCHAR(300)   NOT NULL
created_at    TIMESTAMP
is_active     BOOLEAN        DEFAULT TRUE
```

### `polls_choice`

```
id            UUID           PK
poll          FK → Poll      CASCADE
text          VARCHAR(100)   NOT NULL
order         SMALLINT       (sıra numarası)
```

### `polls_vote`

```
id            UUID           PK
choice        FK → Choice    CASCADE
session_key   VARCHAR(40)    (anonim kullanıcı takibi için)
user          FK → CustomUser NULL (kayıtlı kullanıcılar için)
ip_address    INET           (fazladan spam koruması)
voted_at      TIMESTAMP
```

> **Çift oy koruması:** Aynı anket için `(poll_id, session_key)` ve `(poll_id, user_id)` çiftleri UNIQUE constraint ile korunur.

---

## URL ve Sayfa Haritası

```
/                          → Ana sayfa — tüm anketlerin feed'i
/poll/<uuid>/              → Anket detay sayfası + oy verme
/poll/create/              → Anket oluşturma (login gerekli)
/poll/<uuid>/results/      → Sonuçlar (oy verdikten sonra yönlendirme)

/accounts/register/        → Kayıt ol
/accounts/login/           → Giriş yap
/accounts/logout/          → Çıkış yap
/accounts/profile/         → Kullanıcı profili (kendi anketleri)
```

---

## Özellik Listesi

### Faz 1 — Temel MVP

- [x] **Anket akışı (Feed):** Tüm anketlerin ters kronolojik sırayla listelenmesi
- [x] **Anket detayı:** Seçenekler ve mevcut oy dağılımı (bar grafik)
- [x] **Oy verme:** Anonim (session) + kayıtlı kullanıcı
- [x] **Çift oy koruması:** Session key + kullanıcı ID kontrolü
- [x] **Kullanıcı kaydı:** E-posta, şifre, kullanıcı adı
- [x] **Kullanıcı girişi / çıkışı**
- [x] **Anket oluşturma:** Soru + 2-5 seçenek formu (dinamik JS ile seçenek ekleme)

### Faz 2 — Kullanılabilirlik İyileştirmeleri

- [ ] **Profil sayfası:** Kullanıcının kendi oluşturduğu anketler
- [ ] **Anket silme:** Sadece sahibi silebilir
- [ ] **Sayfalama / sonsuz scroll:** Ana feed için
- [ ] **Arama:** Anket sorusuna göre basit arama
- [ ] **Süre bazlı anket:** İsteğe bağlı sona erme tarihi

### Faz 3 — Sosyal ve Gelişmiş Özellikler

- [ ] **Paylaşım linki:** Her anket için kopyalanabilir URL
- [ ] **Kategori/etiket:** Anketlere konu etiketi ekleme
- [ ] **Trend anketler:** Oy sayısına göre sıralama
- [ ] **Moderasyon:** Admin panelinden anket kaldırma

---

## Arayüz Rehberi

### Renk Paleti

```css
:root {
  /* Arkaplan */
  --bg-primary:   #FAFAFA;   /* Açık kırık beyaz */
  --bg-card:      #FFFFFF;   /* Kart arkaplanı */

  /* Birincil Vurgu */
  --accent-1:     #6C63FF;   /* Canlı mor-mavi (ana CTA) */
  --accent-2:     #FF6584;   /* Canlı pembe-kırmızı (ikincil vurgu) */
  --accent-3:     #43C6AC;   /* Canlı teal-yeşil (başarı, bar grafik) */

  /* Ton üstü katmanları */
  --accent-1-soft: rgba(108, 99, 255, 0.12);
  --accent-2-soft: rgba(255, 101, 132, 0.12);

  /* Metin */
  --text-primary:   #1A1A2E;
  --text-secondary: #6B7280;

  /* Çerçeve */
  --border:         #E5E7EB;
  --border-radius:  16px;
  --shadow:         0 4px 24px rgba(108,99,255,0.08);
}
```

### Tipografi

```css
/* Font: Google Fonts — Inter veya Nunito */
--font-display: 'Nunito', sans-serif;   /* Logo ve başlıklar */
--font-body:    'Inter', sans-serif;    /* Genel metin */
```

### Bileşen Notları

- **Navbar:** Beyaz arkaplan, altı ince accent-1 kenarlığı, sağda giriş/kayıt butonları
- **Anket kartı:** Gölgeli yuvarlak köşeli kart, kullanıcı adı + tarih üstte, soru büyük ve kalın, seçenekler pill-shape butonlar
- **Oy sonuç barı:** `accent-3` rengiyle dolup animasyonlu büyüyen progress bar
- **CTA butonu:** `accent-1` arkaplan, beyaz metin, hover'da hafif yukarı kayan (transform) efekti
- **Form elemanları:** Minimal, altı çizgili ya da hafif borderli, focus'ta accent-1 border

### Responsive Tasarım

- **Mobil öncelikli** tek sütun
- Tablet ve üstünde: Ortalanmış tek sütun, max-width: 680px

---

## Faz Planı

### 🟢 Faz 1 — Temel MVP (Önce Bu)

**Hedef:** Çalışan, deploy edilebilir bir prototip.

**Sıra:**
1. Django projesi + Supabase bağlantısı kurulumu
2. `CustomUser` modeli + kayıt/giriş/çıkış
3. `Poll`, `Choice`, `Vote` modelleri + migrasyonlar
4. Ana feed view + template
5. Anket detay + oy verme view + çift oy koruması
6. Anket oluşturma formu (JS ile dinamik seçenek ekleme)
7. Temel CSS (renk paleti + kart layout)
8. Vercel deploy

**Prompt örneği (Antigravity'ye verilecek):**
```
Faz 1'i uygula:
- Django projesi "kararsizim" olarak başlat
- Supabase PostgreSQL'e bağlan (.env'den DATABASE_URL oku)
- accounts/CustomUser (username, email, password)
- polls/Poll, Choice, Vote modelleri + migrasyonlar
- Tüm view'lar ve URL'ler
- Base template + index, detail, create, login, register sayfaları
- Temel CSS (proje planındaki renk paletini kullan)
- vercel.json ve build_files.sh ekle
```

---

### 🟡 Faz 2 — Kullanılabilirlik

**Prompt örneği:**
```
Faz 2'yi uygula:
- Profil sayfası: kullanıcının kendi anketleri
- Anket silme (sadece sahibi)
- Ana feed'de sayfalama (Django Paginator)
- Anket arama (GET parametresi ile)
```

---

### 🔵 Faz 3 — Sosyal Özellikler

**Prompt örneği:**
```
Faz 3'ü uygula:
- Her ankete kopyalanabilir paylaşım linki
- Anketlere etiket ekleme + etikete göre filtreleme
- Ana sayfada "Trend" sekmesi (oy sayısına göre)
- Django admin panelinde moderasyon araçları
```

---

## Ortam Değişkenleri

`.env.example` dosyası aşağıdaki biçimde olmalıdır:

```env
# Django
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Supabase / PostgreSQL
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# İzin verilen hostlar (prod'da Vercel domain'i ekle)
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Deployment (Vercel)

### `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "kararsizim/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
      }
    },
    {
      "src": "build_files.sh",
      "use": "@vercel/static-build",
      "config": { "distDir": "staticfiles" }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "kararsizim/wsgi.py"
    }
  ]
}
```

### `build_files.sh`

```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### Vercel Ortam Değişkenleri

Vercel dashboard'da şu değişkenler eklenmelidir:

| Değişken | Değer |
|---|---|
| `SECRET_KEY` | Güçlü rastgele string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Supabase connection string |
| `ALLOWED_HOSTS` | `.vercel.app,your-custom-domain.com` |

---

## Geliştirici Notları

- **Anonim oy:** Django'nun `request.session.session_key` kullanılacak. İlk istekte `request.session.create()` çağrılması gerekebilir.
- **UUID primary key:** Güvenlik ve Supabase uyumluluğu için modellerde `uuid` kullanılması önerilir.
- **WhiteNoise:** Production'da statik dosya sunumu için `whitenoise` middleware eklenecek.
- **CSRF:** Oy verme POST istekleri Django'nun CSRF korumasını kullanacak (template'lerde `{% csrf_token %}`).
- **Form validasyonu:** Seçenek sayısı (2-5) hem JS (client-side) hem Django form (server-side) tarafında doğrulanacak.

---

*Son güncelleme: Eylül 2026 | Proje: Kararsızım*
