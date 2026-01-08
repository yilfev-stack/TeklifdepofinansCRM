# DEMART Teklif Yönetim Sistemi - Local Kurulum Rehberi

## 📋 Gereksinimler

```bash
✅ Node.js v18+ (https://nodejs.org/)
✅ Python 3.9+ (https://www.python.org/)
✅ MongoDB Community Edition (https://www.mongodb.com/try/download/community)
✅ Yarn (npm install -g yarn)
✅ Git
```

## 🚀 Kurulum Adımları

### 1. MongoDB'yi Başlatın

**Windows:**
```powershell
net start MongoDB
```

**macOS:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

**MongoDB'yi Test Edin:**
```bash
mongosh --eval "db.adminCommand('ping')"
# Çıktı: { ok: 1 } görmelisiniz
```

### 2. Backend Kurulumu

```bash
cd backend

# Virtual environment oluşturun
python -m venv venv

# Virtual environment'ı aktifleştirin
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies'leri kurun
pip install -r requirements.txt

# .env dosyasını kontrol edin (zaten var olmalı)
# İçeriği:
# MONGO_URL="mongodb://localhost:27017"
# DB_NAME="test_database"
# CORS_ORIGINS="*"

# Backend'i başlatın
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Backend şu adreste çalışacak: **http://localhost:8001**

### 3. Frontend Kurulumu

**YENİ Terminal Açın:**

```bash
cd frontend

# Dependencies'leri kurun
yarn install

# .env dosyasını kontrol edin
# İçeriği şöyle olmalı:
# REACT_APP_BACKEND_URL=http://localhost:8001
# REACT_APP_ENABLE_VISUAL_EDITS=false
# ENABLE_HEALTH_CHECK=false

# Frontend'i başlatın
yarn start
```

Frontend şu adreste açılacak: **http://localhost:3000**

## 🔧 Sorun Giderme

### Problem 1: "Port already in use" hatası

**Backend (8001):**
```bash
# Windows:
netstat -ano | findstr :8001
taskkill /PID [PID_NUMARASI] /F

# macOS/Linux:
lsof -ti:8001 | xargs kill -9
```

**Frontend (3000):**
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID [PID_NUMARASI] /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

### Problem 2: MongoDB bağlanamıyor

```bash
# MongoDB'nin çalıştığını kontrol edin
mongosh

# Çalışmıyorsa tekrar başlatın:
# Windows:
net stop MongoDB
net start MongoDB

# macOS:
brew services restart mongodb-community

# Linux:
sudo systemctl restart mongod
```

### Problem 3: CORS hatası

Backend `.env` dosyasında:
```
CORS_ORIGINS="http://localhost:3000"
```

veya tüm originlere izin vermek için:
```
CORS_ORIGINS="*"
```

### Problem 4: "Module not found" hatası

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules yarn.lock
yarn install
```

### Problem 5: "Yeni Teklif Ekle" çalışmıyor

1. **Frontend .env kontrolü:**
```bash
cat frontend/.env
# REACT_APP_BACKEND_URL=http://localhost:8001 olmalı
```

2. **Backend'in çalıştığını test edin:**
```bash
curl http://localhost:8001/api/customers
```

3. **Browser Console'u kontrol edin:**
- Chrome/Edge: F12 > Console
- Hata mesajlarını kontrol edin

4. **Network Tab'i kontrol edin:**
- F12 > Network
- "Preserve log" aktif edin
- Yeni teklif eklemeyi deneyin
- Kırmızı (failed) istekler var mı kontrol edin

## 📊 İlk Veri Oluşturma

1. **Müşteri Ekle:** http://localhost:3000/customers → "Add New Customer"
2. **Ürün Ekle:** http://localhost:3000/products → "Add New Product"
3. **DEMART Yetkilisi Ekle:** http://localhost:3000/representatives → "Add New Representative"
4. **Teklif Oluştur:** http://localhost:3000/quotations/sales → "Create New Quotation"

## 🔍 API Endpoint Testleri

```bash
# Customers
curl http://localhost:8001/api/customers

# Products
curl http://localhost:8001/api/products

# Representatives
curl http://localhost:8001/api/representatives

# Quotations
curl http://localhost:8001/api/quotations

# Yeni teklif oluşturma testi
curl -X POST http://localhost:8001/api/quotations \
  -H "Content-Type: application/json" \
  -d '{
    "quotation_type": "sales",
    "customer_id": "test-customer-id",
    "subject": "Test Teklifi",
    "validity_days": 30,
    "language": "turkish",
    "line_items": []
  }'
```

## 📁 Önemli Dosyalar

```
/app
├── backend/
│   ├── server.py           # Ana backend dosyası
│   ├── models.py           # Veri modelleri
│   ├── requirements.txt    # Python bağımlılıkları
│   └── .env               # Backend ayarları (GİZLİ!)
├── frontend/
│   ├── src/
│   │   ├── pages/         # React sayfaları
│   │   └── components/    # React bileşenleri
│   ├── public/
│   │   └── images/        # Logolar (demart, sofis, background)
│   ├── package.json       # Node bağımlılıkları
│   └── .env              # Frontend ayarları (GİZLİ!)
├── uploads/              # Yüklenen dosyalar
└── LOCAL_SETUP.md        # Bu dosya
```

## ✅ Çalışma Kontrolü

Aşağıdaki adımların hepsi başarılı olmalı:

1. ✅ MongoDB ping test başarılı
2. ✅ Backend http://localhost:8001 çalışıyor
3. ✅ Frontend http://localhost:3000 açılıyor
4. ✅ Müşteri eklenebiliyor
5. ✅ Ürün eklenebiliyor
6. ✅ DEMART yetkilisi eklenebiliyor
7. ✅ Yeni teklif oluşturulabiliyor

## 🆘 Yardım

Hala sorun yaşıyorsanız:

1. **Browser Console'u kontrol edin** (F12)
2. **Network Tab'i kontrol edin** (F12 > Network)
3. **Backend loglarını kontrol edin** (terminal çıktısı)
4. **MongoDB'nin çalıştığını doğrulayın**

## 🎯 Production'a Dönmek

Eğer tekrar production URL'ine dönmek isterseniz:

**frontend/.env:**
```
REACT_APP_BACKEND_URL=https://pdffix-2.preview.emergentagent.com
```

Sonra frontend'i yeniden başlatın:
```bash
cd frontend
yarn start
```
