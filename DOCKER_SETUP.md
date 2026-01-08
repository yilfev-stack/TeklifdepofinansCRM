# DEMART Teklif Yönetim Sistemi - Docker Kurulumu

## 📋 Gereksinimler

- Docker Desktop (https://www.docker.com/products/docker-desktop/)
- Docker Compose v2+

## 🚀 Hızlı Başlangıç

### 1. Projeyi İndirin
```bash
git clone [your-repo-url]
cd teklif-finali-main
```

### 2. Environment Dosyalarını Hazırlayın

**Backend (.env):**
```bash
cd backend
copy .env.local.example .env
# veya Linux/Mac:
# cp .env.local.example .env
```

**Frontend (.env):**
```bash
cd ../frontend
copy .env.local.example .env
# veya Linux/Mac:
# cp .env.local.example .env
```

**Önemli:** `.env` dosyalarında aşağıdaki değerlerin doğru olduğundan emin olun:

**backend/.env:**
```env
MONGO_URL=mongodb://mongodb:27017
DB_NAME=demart_quotations
CORS_ORIGINS=http://localhost:3000
```

**frontend/.env:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Docker Container'ları Başlatın

```bash
# Ana dizinde (teklif-finali-main)
docker-compose up -d
```

Bu komut şunları yapacak:
- MongoDB container'ı oluşturup başlatacak (port 27017)
- Backend container'ı oluşturup başlatacak (port 8001)
- Frontend container'ı oluşturup başlatacak (port 3000)

### 4. Logları Kontrol Edin

```bash
# Tüm servislerin loglarını görüntüle
docker-compose logs -f

# Sadece backend loglarını görüntüle
docker-compose logs -f backend

# Sadece frontend loglarını görüntüle
docker-compose logs -f frontend
```

### 5. Uygulamayı Açın

Tarayıcınızda şu adresi açın:
**http://localhost:3000**

## 🔧 Yararlı Komutlar

### Container'ları Yönetme

```bash
# Container'ları başlat
docker-compose up -d

# Container'ları durdur
docker-compose down

# Container'ları durdur ve volume'leri temizle
docker-compose down -v

# Container'ları yeniden başlat
docker-compose restart

# Container'ları yeniden build et
docker-compose build

# Build edip başlat
docker-compose up -d --build
```

### Logları İzleme

```bash
# Tüm loglar
docker-compose logs -f

# Sadece backend
docker-compose logs -f backend

# Sadece frontend
docker-compose logs -f frontend

# Sadece MongoDB
docker-compose logs -f mongodb
```

### Container İçine Girmek

```bash
# Backend container'ına gir
docker-compose exec backend bash

# Frontend container'ına gir
docker-compose exec frontend sh

# MongoDB container'ına gir
docker-compose exec mongodb mongosh
```

### Database İşlemleri

```bash
# MongoDB'ye bağlan
docker-compose exec mongodb mongosh demart_quotations

# Database'i temizle
docker-compose exec mongodb mongosh demart_quotations --eval "db.dropDatabase()"

# Collection'ları listele
docker-compose exec mongodb mongosh demart_quotations --eval "db.getCollectionNames()"
```

## 🔄 Kod Değişikliklerini Görmek

Docker volume mount sayesinde kod değişiklikleri otomatik yansır:
- **Backend**: Uvicorn `--reload` ile çalışıyor
- **Frontend**: React hot reload aktif

Sadece kod değiştirin, container'lar otomatik yenilenecek!

## 🐛 Sorun Giderme

### Port Zaten Kullanımda

**Sorun**: "port is already allocated" hatası

**Çözüm**:
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8001
netstat -ano | findstr :27017

# Çıkan PID'yi kullanarak process'i kapat
taskkill /PID [PID_NUMARASI] /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:27017 | xargs kill -9
```

### Container Başlamıyor

**Sorun**: Container sürekli restart oluyor

**Çözüm**:
```bash
# Logları kontrol et
docker-compose logs backend
docker-compose logs frontend

# Container'ı temizle ve yeniden başlat
docker-compose down
docker-compose up -d --build
```

### MongoDB Bağlantı Hatası

**Sorun**: Backend MongoDB'ye bağlanamıyor

**Çözüm**:
```bash
# MongoDB container'ının çalıştığını kontrol et
docker-compose ps

# MongoDB loglarını kontrol et
docker-compose logs mongodb

# Backend .env dosyasını kontrol et
# MONGO_URL=mongodb://mongodb:27017 olmalı (mongodb servis adı)
```

### Frontend Başlamıyor

**Sorun**: Frontend port 3000'de açılmıyor

**Çözüm**:
```bash
# Frontend loglarını kontrol et
docker-compose logs frontend

# node_modules'u temizle ve yeniden build et
docker-compose down
docker-compose build frontend --no-cache
docker-compose up -d
```

### Yavaş Çalışıyor

**Sorun**: Docker'da yavaş çalışıyor

**Çözüm**:
```bash
# Docker Desktop'ta Resources > Advanced bölümünden
# CPU ve Memory limitlerini artırın

# Önerilen:
# - CPUs: 4
# - Memory: 8 GB
```

## 📊 Container Durumunu Kontrol Etme

```bash
# Çalışan container'ları listele
docker-compose ps

# Container kaynak kullanımını göster
docker stats

# Container'ların health check'ini göster
docker-compose ps
```

## 🧹 Temizlik

### Geliştirme Sonrası Temizlik
```bash
# Container'ları durdur
docker-compose down

# Volume'leri de sil (VERİLER SİLİNİR!)
docker-compose down -v
```

### Tam Temizlik
```bash
# UYARI: TÜM Docker verileri silinir!

# Kullanılmayan image'leri sil
docker image prune -a

# Kullanılmayan volume'leri sil
docker volume prune

# Her şeyi temizle
docker system prune -a --volumes
```

## 🔐 Production için Notlar

Bu Docker setup **sadece development içindir**. Production için:

1. **Multi-stage build** kullanın
2. **Optimized images** kullanın (alpine, distroless)
3. **Environment variables** güvenli yönetin
4. **Volume permissions** düzeltin
5. **Health checks** ekleyin
6. **Resource limits** belirleyin
7. **Logging** düzgün yapılandırın

## 📞 Yardım

Sorun yaşıyorsanız:
1. Logları kontrol edin: `docker-compose logs -f`
2. Container durumunu kontrol edin: `docker-compose ps`
3. Network'ü kontrol edin: `docker network inspect teklif-finali-main_demart-network`

## ✅ Çalışma Kontrolü

Aşağıdaki adımlar başarılı olmalı:

1. ✅ `docker-compose ps` → 3 container çalışıyor (mongodb, backend, frontend)
2. ✅ http://localhost:8001/api/customers → API çalışıyor
3. ✅ http://localhost:3000 → Frontend açılıyor
4. ✅ Müşteri, ürün, teklif eklenebiliyor
5. ✅ Kod değişiklikleri otomatik yansıyor
