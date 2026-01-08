#!/bin/bash

echo "=================================="
echo "DEĞIŞIKLIK KONTROLÜ"
echo "=================================="
echo ""

echo "1. Git son commit tarihi:"
git log -1 --format="%ci - %s"
echo ""

echo "2. Değiştirilen dosyalar (son commit):"
git show --name-only --oneline | tail -n +2
echo ""

echo "3. CreateQuotation.js header kontrolü:"
grep -n "Add Item, Cancel, Save" frontend/src/pages/CreateQuotation.js | head -1
echo ""

echo "4. EditQuotation.js header kontrolü:"
grep -n "Revision Dropdown, Add Item" frontend/src/pages/EditQuotation.js | head -1
echo ""

echo "5. QuotationFiles.js render kontrolü:"
grep -n "categoryFiles.length" frontend/src/components/QuotationFiles.js | head -1
echo ""

echo "6. QuotationPreview.js dil badge kontrolü:"
grep -n "TR - TÜRKÇE" frontend/src/pages/QuotationPreview.js | head -1
echo ""

echo "=================================="
echo "DOCKER DURUMU"
echo "=================================="
echo ""

echo "7. Çalışan container'lar:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=================================="
echo "SONUÇ"
echo "=================================="
if grep -q "TR - TÜRKÇE" frontend/src/pages/QuotationPreview.js && \
   grep -q "categoryFiles.length" frontend/src/components/QuotationFiles.js; then
    echo "✅ Kod değişiklikleri mevcut!"
    echo ""
    echo "Şimdi yapılması gerekenler:"
    echo "1. docker-compose down"
    echo "2. docker-compose build --no-cache"
    echo "3. docker-compose up -d"
    echo "4. Browser'da Ctrl+Shift+R (hard refresh)"
else
    echo "❌ Kod değişiklikleri eksik! Git pull yapın."
fi
