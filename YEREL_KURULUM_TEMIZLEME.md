# Yerel Kurulum - Tam Temizleme ve Güncelleme

## Adım 1: Tüm Container'ları Durdurun ve Silin
```bash
cd /path/to/your/project  # Projenizin bulunduğu klasör

# Tüm container'ları durdur
docker-compose down

# Container'ları, volume'leri ve image'leri temizle
docker-compose down -v --rmi all

# Tüm build cache'i temizle
docker builder prune -af
```

## Adım 2: Yerel Cache'leri Temizle
```bash
# Frontend node_modules ve build klasörlerini sil
rm -rf frontend/node_modules
rm -rf frontend/build
rm -rf frontend/.cache

# Backend cache'lerini temizle
rm -rf backend/__pycache__
rm -rf backend/**/__pycache__
```

## Adım 3: GitHub'dan Güncel Kodu Çekin
```bash
git pull origin main  # veya master

# Değişiklikleri kontrol edin
git log --oneline -3
```

## Adım 4: Yeniden Build Edin (Cache Kullanmadan)
```bash
# Cache kullanmadan build et
docker-compose build --no-cache

# Container'ları başlat
docker-compose up -d

# Log'ları takip edin (sorun varsa göreceksiniz)
docker-compose logs -f
```

## Adım 5: Browser Cache'ini Temizle
1. Chrome/Firefox'ta `Ctrl + Shift + R` (Hard Refresh)
2. Veya Developer Tools açın (F12) > Network sekmesi > "Disable cache" işaretleyin
3. Sayfayı yenileyin

## Adım 6: Test Edin

### Butonları Kontrol Et
- http://localhost:3001/quotations/sales/create
  - Üst sağda: **Add Item, Cancel, Save** butonları olmalı

- Bir teklifi edit edin:
  - Üst sağda: **Revision Dropdown, Add Item, Cancel, Save, New Revision, Update Status, Preview** butonları olmalı

### Dosya Kategorilendirmesini Test Et
1. Bir teklifi önizleyin
2. "Dosyalar" sekmesine tıklayın
3. "Gelen Maliyetler" kategorisine bir dosya yükleyin
4. "Giden Maliyetler" kategorisine başka bir dosya yükleyin
5. Her dosyanın kendi kategorisinde göründüğünü kontrol edin

### PDF Dil Badge'ini Kontrol Et
1. Türkçe bir teklifi önizleyin
2. Aşağı kaydırın, "TR - TÜRKÇE" yazan kırmızı kutu görmeli
3. "Download PDF" butonuna tıklayın
4. PDF'i açın ve kırmızı kutuyu kontrol edin

## Sorun Çözülmediyse

### Port çakışması olabilir:
```bash
# 3001 ve 8002 portlarını kontrol edin
lsof -i :3001
lsof -i :8002

# Çakışan process'leri kapatın
kill -9 <PID>
```

### Frontend build hatası varsa:
```bash
# Frontend container'a girin
docker-compose exec frontend sh

# Manuel build yapın
yarn build

# Çıkın
exit
```

### Backend hatası varsa:
```bash
# Backend log'larını kontrol edin
docker-compose logs backend

# Backend container'a girin
docker-compose exec backend sh

# Paketleri kontrol edin
pip list

# Çıkın
exit
```

## Hala Çalışmazsa

1. **Tüm Docker kaynaklarını temizleyin:**
```bash
docker system prune -af --volumes
```

2. **Projeyi sıfırdan klonlayın:**
```bash
cd ..
rm -rf eski-proje-klasoru
git clone <repository-url> yeni-proje
cd yeni-proje
docker-compose up --build
```

3. **Browser'ı tamamen kapatıp tekrar açın** (tüm sekmeler)

4. **Gizli/Incognito modda test edin**

## Başarılı Kurulum Kontrol Listesi

✅ `docker-compose ps` komutu 3 container göstermeli (frontend, backend, mongodb)
✅ http://localhost:3001 açılmalı
✅ Backend API'si http://localhost:8002/api/quotations çalışmalı
✅ Create ve Edit sayfalarında doğru butonlar görünmeli
✅ Dosya yükleme kategorilere göre çalışmalı
✅ PDF'de "TR - TÜRKÇE" badge'i görünmeli (boş kutu değil)

## İletişim

Hala sorun yaşıyorsanız:
1. `docker-compose logs` çıktısını paylaşın
2. Browser console log'larını (F12 > Console) paylaşın
3. Hangi adımda hata aldığınızı belirtin
