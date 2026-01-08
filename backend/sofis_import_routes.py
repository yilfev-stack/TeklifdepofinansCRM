"""
SOFIS Akıllı Import Sistemi
- Ürün kodu (SKU) odaklı karşılaştırma
- Yeni ürün, fiyat değişikliği, aynı kalan tespiti
- Excel sayfa isimlerine göre otomatik gruplama
- Toplu veya tek tek güncelleme
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import pandas as pd
import io

router = APIRouter(tags=["SOFIS Import"])

_db = None

def set_database(db):
    global _db
    _db = db


# Sayfa ismi -> Grup ismi eşleştirme
SHEET_TO_GROUP = {
    'SFC Interlocking': 'SFC Interlocking',
    'NL Interlocking': 'NL Interlocking',
    'Drive Systems': 'Drive Systems',
    'LockoutTagout': 'LockoutTagout',
    'Lockout Tagout': 'LockoutTagout',
}

def parse_sofis_excel(content):
    """Parse all sheets from SOFIS Excel and return products by SKU with group info"""
    xlsx = pd.ExcelFile(io.BytesIO(content))
    
    brand_map = {
        'SFC Interlocking': 'SFC',
        'SFC': 'SFC',
        'NL Interlocking': 'NL',
        'NL': 'NL',
        'Drive Systems': 'Drive Systems',
        'LockoutTagout': 'Lockout Tagout',
        'Lockout Tagout': 'Lockout Tagout',
    }
    
    products_by_sku = {}  # SKU -> product info
    groups_found = set()  # Bulunan gruplar
    
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
        brand = brand_map.get(sheet_name, sheet_name)
        group_name = SHEET_TO_GROUP.get(sheet_name, sheet_name)  # Sayfa ismi = Grup ismi
        groups_found.add(group_name)
        current_category = ""
        
        for idx, row in df.iterrows():
            if idx < 8:
                continue
                
            product_code = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            description = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ''
            price_val = row.iloc[5] if len(row) > 5 else None
            
            if not product_code or product_code == 'nan' or product_code == 'Product#':
                continue
            
            # Category detection
            if pd.isna(price_val) or str(price_val) in ['nan', '']:
                if not description or description == 'nan':
                    current_category = product_code
                    continue
            
            try:
                price = float(price_val) if pd.notna(price_val) else 0
            except (ValueError, TypeError):
                continue
                
            if price <= 0:
                continue
            
            # SKU is the key - uppercase for consistency
            sku = product_code.upper()
            
            # If same SKU exists in multiple sheets, keep the one with price
            if sku not in products_by_sku or products_by_sku[sku]['cost_price'] == 0:
                products_by_sku[sku] = {
                    'sku': sku,
                    'product_code': product_code,
                    'description': description,
                    'category': current_category,
                    'brand': brand,
                    'group_name': group_name,  # YENİ: Grup bilgisi
                    'cost_price': price,
                    'currency': 'EUR',
                    'sheet': sheet_name
                }
    
    return products_by_sku, list(groups_found)


@router.post("/analyze")
async def analyze_sofis_excel(file: UploadFile = File(...)):
    """
    Analyze SOFIS Excel and compare with existing products.
    Returns categorized comparison report with group info.
    """
    _require_db()
    
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyası yüklenebilir")
    
    try:
        content = await file.read()
        
        # Parse Excel - now returns groups too
        excel_products, groups_found = parse_sofis_excel(content)
        
        # Get existing SOFIS products from DB
        existing_products = await _db.products.find(
            {"is_sofis_import": True},
            {"_id": 0}
        ).to_list(1000)
        
        # Build SKU -> DB product map
        db_by_sku = {}
        for p in existing_products:
            for model in p.get('models', []):
                sku = model.get('sku', '').upper()
                if sku:
                    db_by_sku[sku] = {
                        'product_id': p['id'],
                        'cost_price': model.get('cost_price', 0),
                        'description': p.get('item_description', ''),
                        'brand': p.get('brand', ''),
                        'category': p.get('category', ''),
                        'group_id': p.get('group_id', '')
                    }
        
        # Compare and categorize
        new_products = []      # In Excel but not in DB
        price_changed = []     # In both, price different
        price_same = []        # In both, price same
        removed_products = []  # In DB but not in Excel
        
        # Check Excel products against DB
        for sku, excel_p in excel_products.items():
            if sku in db_by_sku:
                db_p = db_by_sku[sku]
                old_price = db_p['cost_price']
                new_price = excel_p['cost_price']
                
                if abs(old_price - new_price) > 0.01:  # Price changed
                    change_percent = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
                    price_changed.append({
                        **excel_p,
                        'product_id': db_p['product_id'],
                        'old_price': old_price,
                        'new_price': new_price,
                        'change_percent': round(change_percent, 1),
                        'change_amount': round(new_price - old_price, 2)
                    })
                else:  # Price same
                    price_same.append({
                        **excel_p,
                        'product_id': db_p['product_id'],
                        'current_price': old_price
                    })
            else:
                # New product
                new_products.append(excel_p)
        
        # Check DB products not in Excel
        for sku, db_p in db_by_sku.items():
            if sku not in excel_products:
                removed_products.append({
                    'sku': sku,
                    'product_id': db_p['product_id'],
                    'description': db_p['description'],
                    'brand': db_p['brand'],
                    'cost_price': db_p['cost_price']
                })
        
        return {
            'ok': True,
            'filename': file.filename,
            'groups_found': groups_found,  # YENİ: Bulunan gruplar
            'summary': {
                'total_in_excel': len(excel_products),
                'total_in_db': len(db_by_sku),
                'new_products': len(new_products),
                'price_changed': len(price_changed),
                'price_same': len(price_same),
                'removed_from_list': len(removed_products),
                'groups_count': len(groups_found)
            },
            'new_products': new_products,
            'price_changed': price_changed,
            'price_same': price_same,
            'removed_products': removed_products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya analiz hatası: {str(e)}")


@router.post("/apply")
async def apply_sofis_changes(data: dict = Body(...)):
    """
    Apply selected changes from analysis.
    Automatically creates groups based on Excel sheet names and assigns products.
    
    Expected data:
    {
        "add_new": [{"sku": "...", "description": "...", "group_name": "...", ...}, ...],
        "update_prices": [{"sku": "...", "product_id": "...", "new_price": 123, "group_name": "..."}, ...],
        "groups_found": ["SFC Interlocking", "NL Interlocking", ...],
        "skip": ["SKU1", "SKU2", ...]  # Optional - products to skip
    }
    """
    _require_db()
    
    add_new = data.get('add_new', [])
    update_prices = data.get('update_prices', [])
    groups_found = data.get('groups_found', [])
    
    added = 0
    updated = 0
    groups_created = 0
    errors = []
    
    # Step 1: Create groups if they don't exist
    group_id_map = {}  # group_name -> group_id
    
    for group_name in groups_found:
        if not group_name:
            continue
            
        # Check if group exists
        existing_group = await _db.product_groups.find_one({"name": group_name})
        
        if existing_group:
            group_id_map[group_name] = existing_group['id']
        else:
            # Create new group
            new_group = {
                "id": str(uuid4()),
                "name": group_name,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await _db.product_groups.insert_one(new_group)
            group_id_map[group_name] = new_group['id']
            groups_created += 1
    
    # Step 2: Add new products with group assignment
    for p in add_new:
        try:
            sku = p.get('sku', '').strip().upper()
            if not sku:
                continue
            
            # Check if already exists
            exists = await _db.products.find_one({"models.sku": sku})
            if exists:
                continue
            
            # Get group_id from group_name
            group_name = p.get('group_name', '')
            group_id = group_id_map.get(group_name, '')
            
            new_product = {
                "id": str(uuid4()),
                "product_type": "sales",
                "brand": p.get('brand', 'SOFIS'),
                "category": p.get('category', ''),
                "group_id": group_id,  # YENİ: Grup ataması
                "item_short_name": p.get('description', sku)[:100],
                "item_description": p.get('description', ''),
                "default_unit": "Adet",
                "default_currency": p.get('currency', 'EUR'),
                "default_unit_price": p.get('cost_price', 0),
                "cost_price": p.get('cost_price', 0),
                "is_active": True,
                "is_sofis_import": True,
                "models": [{
                    "id": str(uuid4()),
                    "model_name": p.get('product_code', sku),
                    "sku": sku,
                    "price": p.get('cost_price', 0),
                    "cost_price": p.get('cost_price', 0)
                }],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await _db.products.insert_one(new_product)
            added += 1
            
        except Exception as e:
            errors.append(f"Ekleme hatası {p.get('sku', '?')}: {str(e)}")
    
    # Step 3: Update prices AND assign groups for existing products
    for p in update_prices:
        try:
            product_id = p.get('product_id')
            new_price = float(p.get('new_price', 0))
            sku = p.get('sku', '').upper()
            group_name = p.get('group_name', '')
            group_id = group_id_map.get(group_name, '')
            
            if not product_id:
                continue
            
            product = await _db.products.find_one({"id": product_id})
            if not product:
                continue
            
            models = product.get('models', [])
            for model in models:
                if model.get('sku', '').upper() == sku:
                    model['cost_price'] = new_price
                    model['price'] = new_price  # Reset sale price to cost (user sets markup in quotation)
                    break
            
            update_data = {
                "models": models,
                "cost_price": new_price,
                "default_unit_price": new_price,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Update group if provided
            if group_id:
                update_data["group_id"] = group_id
            
            await _db.products.update_one(
                {"id": product_id},
                {"$set": update_data}
            )
            updated += 1
            
        except Exception as e:
            errors.append(f"Güncelleme hatası {p.get('sku', '?')}: {str(e)}")
    
    # Step 4: Also update groups for products with same price
    price_same = data.get('price_same', [])
    groups_updated = 0
    
    for p in price_same:
        try:
            product_id = p.get('product_id')
            group_name = p.get('group_name', '')
            group_id = group_id_map.get(group_name, '')
            
            if product_id and group_id:
                result = await _db.products.update_one(
                    {"id": product_id, "group_id": {"$ne": group_id}},  # Only if different
                    {"$set": {"group_id": group_id}}
                )
                if result.modified_count > 0:
                    groups_updated += 1
        except:
            pass
    
    return {
        'ok': True,
        'added': added,
        'updated': updated,
        'groups_created': groups_created,
        'groups_updated': groups_updated,
        'errors': errors[:10],
        'message': f"{added} yeni ürün eklendi, {updated} fiyat güncellendi, {groups_created} grup oluşturuldu"
    }


@router.get("/products")
async def list_sofis_products(brand: Optional[str] = None):
    """List all SOFIS imported products"""
    _require_db()
    
    query = {"is_sofis_import": True}
    if brand:
        query["brand"] = brand
    
    products = await _db.products.find(query, {"_id": 0}).to_list(1000)
    return products


@router.get("/stats")
async def get_sofis_stats():
    """Get SOFIS products statistics"""
    _require_db()
    
    # Count by brand
    pipeline = [
        {"$match": {"is_sofis_import": True}},
        {"$group": {"_id": "$brand", "count": {"$sum": 1}}}
    ]
    
    brand_stats = await _db.products.aggregate(pipeline).to_list(10)
    
    total = sum(b['count'] for b in brand_stats)
    
    return {
        'total_products': total,
        'by_brand': {b['_id']: b['count'] for b in brand_stats}
    }


def _require_db():
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
