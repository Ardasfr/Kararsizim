# 🤔 Kararsızım — Hızlı Karar & Topluluk Anketleri

[![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Kararsızım**, günlük hayatta iki veya daha fazla seçenek arasında kararsız kalan kullanıcıların topluluktan anında oy ve fikir almasını, ya da interaktif **Karar Çarkı** ile saniyeler içinde eğlenceli ve adil kararlar vermesini sağlayan modern bir web platformudur.

---

## ✨ Temel Özellikler

### 🎡 1. Karar Çarkı (Decision Wheel)
* **Özel Çark Oluşturma**: Giriş yapan kullanıcılar diledikleri başlık, açıklama ve 2 ila 20 seçenek belirleyerek kendi çarklarını oluşturabilir.
* **60-120 FPS Donanım Hızlandırmalı Çark Motoru**: Offscreen buffer canvas mimarisi sayesinde sıfır layout thrashing ve pürüzsüz animasyon performansı.
* **Kusursuz Matematiksel İğne Hizalaması**: Çarkın üst ibresi ($3\pi/2$) ile kazanan dilim %100 örtüşür; belirsizlik veya görsel kayma yaşanmaz.
* **Web Audio API Ses Efektleri**: Harici ses dosyası indirmeden, tarayıcı işlemcisiyle sentezlenen mekanik ahşap tık sesleri ve zafer melodisi.
* **Konfeti & Zafer Ekranı**: Karar verildiğinde kazanan seçenek şık bir tebrik kartı ve konfeti animasyonuyla duyurulur.
* **Misafir Kullanıcı Erişimi**: Üye olmayan kullanıcılar paylaşılan çarkları görüntüleyip diledikleri kadar çevirebilir.
* **Kişiselleştirilmiş Çark Yönetimi**: Profil sayfasından oluşturulan çarklar listelenir, tek tıkla silinebilir.

### 🗳️ 2. Topluluk Anketleri & Oylama
* **Dinamik Seçenekli Anketler**: Kullanıcılar istedikleri sayıda seçenek ekleyerek anket başlatabilir.
* **Anında AJAX Oylama**: Sayfa yenilenmeden, 0ms bekleme süresiyle oy verme ve animasyonlu yüzde çubukları.
* **Trendler & Topluluk Nabzı**: En çok oy alan anketler, günün trendleri ve canlı platform istatistikleri.
* **Kategori & Arama Filtreleme**: Teknoloji, Yaşam, Eğlence, Yemek ve daha birçok kategoride anlık filtreleme ve arama.

### 🌓 3. Kusursuz Senkronize Koyu / Aydınlık Mod
* **Tek Dokunuşla Tema Değişimi**: ☀️ / 🌙 butonu ile akıcı geçiş.
* **%100 Senkronize Yüzey Geçişi**: Navbar, kartlar, yan menü, butonlar ve altbilgi (footer) aynı anda 250ms içinde pürüzsüzce renk değiştirir; parça parça gecikme veya sıçrama olmaz.
* **Döner Buton Mikro-Animasyonu**: Tema butonu tıklandığında ikon kendi etrafında dönerek yaylanır.
* **Anti-FOUC Başlangıç**: Sayfa ilk açılırken kullanıcının tercih ettiği tema beyaz/siyah patlama yapmadan anında yüklenir.

### ♿ 4. Kapsamlı Erişilebilirlik (A11y) Paneli
* **Metin Boyutu Ölçekleme**: Normal (%100), Büyük (%115), Çok Büyük (%130).
* **Yüksek Kontrast Modu**: Maksimum kontrast ve belirgin kenarlıklar.
* **Disleksi Dostu Yazı Tipi**: Okuma güçlüğünü azaltan OpenDyslexic yazı stili.
* **Hareket & Animasyonları Azalt**: Vestibüler hassasiyeti olan kullanıcılar için tüm animasyonları devre dışı bırakma.
* **Bağlantıların Altını Çiz**: Tıklanabilir alanları belirginleştirme.
* **Ayarları Kalıcı Saklama**: `localStorage` entegrasyonuyla tüm ayarlar oturumlar arasında korunur.

### 📱 5. %100 Duyarlı (Responsive) Tasarım
* 320px ultra-kompakt mobil ekranlardan 4K geniş ekranlara kadar sıfır yatay taşma (zero overflow).
* Mobilde daralan butonlar, otomatik korunan Giriş/Kayıt butonları ve dokunmatik optimize kontroller.

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji | Açıklama |
|---|---|---|
| **Backend** | Python 3.12 / Django 5.x | Güçlü MVC mimarisi, güvenli oturum ve ORM |
| **Veritabanı** | PostgreSQL / Supabase | Yüksek performanslı ilişkisel veritabanı |
| **Frontend** | HTML5, Vanilla CSS3, Modern ES6+ | Framework yükü olmadan ultra hızlı, temiz kod |
| **Grafik & Ses** | HTML5 Canvas API, Web Audio API | 60-120 FPS çark renderlama & sentetik sesler |
| **Statik Dosyalar** | WhiteNoise | Gzip/Brotli sıkıştırmalı statik dosya sunumu |
| **Dağıtım (Deployment)** | Vercel Serverless WSGI | Otomatik CI/CD entegrasyonlu bulut barındırma |

---

## 📂 Proje Dizin Yapısı

```text
Kararsizim/
├── accounts/               # Kullanıcı kimlik doğrulama, profil ve üyelik işlemleri
├── polls/                  # Anket oluşturma, oylama, kategoriler ve sosyal akış
├── wheels/                 # Karar Çarkı modelleri, görünümleri ve formları
│   ├── migrations/
│   ├── models.py           # Wheel, WheelOption, WheelSpin modelleri
│   ├── views.py            # Çark listeleme, detay, oluşturma, silme, çevirme
│   └── tests.py            # Çark birim ve entegrasyon testleri
├── kararsizim/             # Django proje yapılandırması
│   ├── settings/
│   │   ├── base.py         # Ortak ayarlar
│   │   ├── development.py  # Yerel geliştirme ayarları
│   │   └── production.py   # Vercel & Supabase canlı ortam ayarları
│   ├── urls.py             # Global yönlendirme
│   └── wsgi.py             # WSGI ve Vercel giriş noktası
├── static/
│   ├── css/
│   │   └── style.css       # Tasarım sistemi, tema değişkenleri, responsive kurallar
│   └── js/
│   │   ├── main.js         # Tema, A11y, AJAX oylama ve UI yardımcıları
│   │   └── wheel.js        # 60-120 FPS Canvas çark motoru ve ses sentezleyici
├── templates/
│   ├── base.html           # Ana iskelet, SEO ve evrensel scriptler
│   ├── partials/           # Navbar, mesajlar, footer, a11y modal
│   ├── accounts/           # Giriş, kayıt, profil şablonları
│   ├── polls/              # Akış, anket detayı, anket oluşturma
│   └── wheels/             # Çark listesi, çark sayfası, yeni çark formu
├── vercel.json             # Vercel derleme ve yönlendirme konfigürasyonu
├── requirements.txt        # Python bağımlılıkları
└── manage.py               # Django yönetim aracı
```

---

## 🚀 Yerel Kurulum & Çalıştırma

### Gereksinimler
- Python 3.10 veya üzeri
- Git
- PostgreSQL (veya Supabase veritabanı bağlantısı)

### Adım Adım Kurulum

1. **Repoyu Klonlayın:**
   ```bash
   git clone https://github.com/Ardasfr/Kararsizim.git
   cd Kararsizim
   ```

2. **Sanal Ortam (Virtual Environment) Oluşturun ve Aktif Edin:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Gerekli Paketleri Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Çevresel Değişkenleri (`.env`) Ayarlayın:**
   Proje kök dizininde bir `.env` dosyası oluşturun:
   ```env
   SECRET_KEY=gizli-anahtariniz-buraya
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DATABASE_URL=postgres://kullanici:sifre@host:5432/veritabani_adi
   ```

5. **Veritabanı Göçlerini (Migrations) Uygulayın:**
   ```bash
   python manage.py migrate --settings=kararsizim.settings.development
   ```

6. **Geliştirme Sunucusunu Başlatın:**
   ```bash
   python manage.py runserver 127.0.0.1:8000 --settings=kararsizim.settings.development
   ```

   Artık tarayıcınızdan **`http://127.0.0.1:8000/`** adresine giderek siteyi kullanabilirsiniz!

---

## 🧪 Testleri Çalıştırma

Tüm anket ve karar çarkı birim/entegrasyon testlerini çalıştırmak için:

```bash
python manage.py test --keepdb --settings=kararsizim.settings.development
```

> 17 birim testin tamamı veritabanı bütünlüğünü, yetkilendirmeleri ve çark oylama mekanizmalarını otomatik olarak doğrular.

---

## ☁️ Canlıya Alma (Vercel Deployment)

Proje Vercel üzerinde sorunsuz çalışacak şekilde yapılandırılmıştır (`vercel.json` ve `kararsizim/wsgi.py`):

1. Reponuzu GitHub'a push edin.
2. [Vercel Dashboard](https://vercel.com/) üzerinden projeyi içe aktarın (Import Project).
3. Ortam Değişkenlerini (Environment Variables) ekleyin:
   * `SECRET_KEY`: Güvenli rastgele anahtar
   * `DEBUG`: `False`
   * `DATABASE_URL`: Canlı Supabase / PostgreSQL bağlantı dizesi
   * `DJANGO_SETTINGS_MODULE`: `kararsizim.settings.production`
4. Deploy butonuna basın; Vercel otomatik olarak derleyip canlıya alacaktır.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Dilediğiniz gibi kullanabilir, geliştirebilir ve katkıda bulunabilirsiniz.
