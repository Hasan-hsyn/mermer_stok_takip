# 🏭 Mermer Fabrikası Stok Takip Sistemi

Python ve Flask kullanılarak geliştirilmiş, mermer fabrikaları için dijital stok yönetim ve takip sistemi.

Bu proje; fabrikadaki mermer blokların kaydını tutmak, stok durumunu anlık izlemek ve QR kod teknolojisi ile fiziksel takibi kolaylaştırmak amacıyla geliştirilmiştir.

## 🚀 Özellikler

* **Detaylı Stok Girişi:** Mermer türü, ton, en, boy, adet ve fotoğraf ile kayıt.
* **Otomatik QR Kod:** Her yeni mermer girişi için otomatik QR kod oluşturur ve linkler.
* **Akıllı Hesaplama:** En/Boy/Adet verisinden otomatik m2 hesabı yapar.
* **Kritik Stok Uyarısı:** Stoğu 20'nin altına düşen ürünler için ana panelde uyarı verir.
* **Kesim Modülü:** Stoktan düşüm (kesim) yapıldığında veritabanını ve toplam m2'yi günceller.
* **Mobil Uyumlu Arayüz:** Tablet ve telefonlardan kolay kullanım için responsive tasarım.

## 🛠️ Kullanılan Teknolojiler

* **Backend:** Python 3, Flask
* **Veritabanı:** SQLite
* **Görüntü İşleme:** Pillow (QR Kodlar için)
* **Frontend:** HTML5, CSS3 (Modern & Kurumsal Tasarım)
### Ekran Görüntüleri

### 1. Ana Sayfa
Sistemimizin ilk giriş sayfası.
![Ana Sayfa](img/ana_sayfa.png)

### 2. Yönetim Paneli
Fabrikanın anlık durumu.
![Yönetim Paneli](img/panel.png)

### 3. Stok Listesi
Depodaki ürünler.
![Stok Listesi](img/stok_listesi.png)

### 4. Mal Kabul
Yeni giriş ekranı.
![Mal Kabul](img/mal_kabul.png)

---
👨‍💻 **Geliştirici:** Hasan Hüseyin
