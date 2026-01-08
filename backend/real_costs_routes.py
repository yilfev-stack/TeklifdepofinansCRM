"""
Real Costs Module - Çoklu Banka & Para Birimi
=============================================
Garanti Bankası + Ziraat Bankası
TL, EUR, USD desteği

Kredi kartı modülü KALDIRILDI - sadece banka hesapları takibi
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Form
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import pandas as pd
import io
import os
from pathlib import Path

router = APIRouter()

# Database reference
_db = None

def set_db(db):
    global _db
    _db = db

def _require_db():
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

# Password for module access
MODULE_PASSWORD = "984027"

# Supported banks and currencies
BANKS = ["Garanti", "Ziraat"]
CURRENCIES = ["TRY", "EUR", "USD"]

# Upload storage directory
UPLOAD_DIR = Path("/app/backend/uploads/real_costs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# AUTHENTICATION
# ============================================================================
@router.post("/verify-password")
async def verify_password(data: dict = Body(...)):
    if data.get("password") == MODULE_PASSWORD:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Yanlış şifre")


# ============================================================================
# BANKS MANAGEMENT
# ============================================================================
@router.get("/banks")
async def get_banks():
    """Get list of supported banks"""
    return {"banks": BANKS, "currencies": CURRENCIES}


# ============================================================================
# OPENING BALANCES - Per Bank/Currency
# ============================================================================
@router.get("/opening-balances")
async def get_opening_balances():
    """Get all opening balances grouped by bank and currency"""
    _require_db()
    balances = await _db.real_costs_opening.find({}, {"_id": 0}).to_list(100)
    
    # Structure: { "Garanti_TRY": 1000, "Garanti_EUR": 500, ... }
    result = {}
    for b in balances:
        key = f"{b['bank']}_{b['currency']}"
        result[key] = {
            "amount": b.get("amount", 0),
            "date": b.get("date"),
            "note": b.get("note")
        }
    return result


@router.post("/opening-balances")
async def set_opening_balance(data: dict = Body(...)):
    """Set opening balance for a specific bank/currency"""
    _require_db()
    
    bank = data.get("bank")
    currency = data.get("currency")
    amount = float(data.get("amount", 0))
    
    if bank not in BANKS:
        raise HTTPException(status_code=400, detail=f"Geçersiz banka. Desteklenen: {BANKS}")
    if currency not in CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Geçersiz para birimi. Desteklenen: {CURRENCIES}")
    
    # Upsert
    await _db.real_costs_opening.update_one(
        {"bank": bank, "currency": currency},
        {"$set": {
            "bank": bank,
            "currency": currency,
            "amount": amount,
            "date": data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "note": data.get("note", ""),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {"ok": True, "message": f"{bank} {currency} açılış bakiyesi kaydedildi"}


# ============================================================================
# PARSING HELPERS
# ============================================================================
def parse_turkish_number(val):
    """Parse Turkish number format"""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    try:
        s = str(val).strip()
        if s == '' or s == 'nan':
            return 0.0
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except:
        return 0.0


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats"""
    formats = ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%y", "%d-%m-%Y", "%d/%m/%y"]
    date_str = str(date_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None


def find_header_row(df, keywords):
    """Find row containing header keywords"""
    for i in range(min(20, len(df))):
        row_vals = [str(v).lower().strip() for v in df.iloc[i].tolist() if pd.notna(v)]
        matches = sum(1 for kw in keywords if any(kw in v for v in row_vals))
        if matches >= 2:
            return i
    return 0


# ============================================================================
# BANK STATEMENT PARSER
# ============================================================================
def parse_bank_statement(df):
    """Parse bank statement - works for both Garanti and Ziraat formats"""
    # Try to find header with various keyword combinations
    header_row = find_header_row(df, ['tarih', 'açıklama', 'tutar', 'bakiye'])
    if header_row == 0:
        # Try Ziraat format keywords
        header_row = find_header_row(df, ['tarih', 'fiş', 'işlem tutarı', 'bakiye'])
    
    if header_row > 0:
        df.columns = [str(c).strip() if not pd.isna(c) else f'Col{i}' for i, c in enumerate(df.iloc[header_row])]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    records = []
    for idx, row in df.iterrows():
        try:
            # Find date
            date_val = None
            for col in ['Tarih', 'tarih']:
                if col in row.index:
                    date_val = row.get(col)
                    break
            
            if pd.isna(date_val) or str(date_val).strip() in ['', 'nan']:
                continue
            
            # Skip footer rows (common in Ziraat)
            date_str = str(date_val).strip()
            if any(skip in date_str.lower() for skip in ['toplam', 'sayfa', 'www.', 'ticaret', 'merkez']):
                continue
            
            # Find amount - support both formats
            amount = 0
            for col in ['Tutar', 'tutar', 'İşlem Tutarı', 'işlem tutarı']:
                if col in row.index:
                    amount = parse_turkish_number(row.get(col))
                    if amount != 0:
                        break
            
            # Find balance after transaction
            balance = None
            for col in ['Bakiye', 'bakiye']:
                if col in row.index:
                    balance = parse_turkish_number(row.get(col))
                    break
            
            # Find description
            description = ''
            for col in ['Açıklama', 'açıklama']:
                if col in row.index and not pd.isna(row.get(col)):
                    description = str(row.get(col)).strip()
                    break
            
            # Find reference - support both Garanti (Dekont No) and Ziraat (Fiş No)
            reference = ''
            for col in ['Dekont No', 'dekont no', 'Fiş No', 'fiş no', 'Referans']:
                if col in row.index and not pd.isna(row.get(col)):
                    reference = str(row.get(col)).strip()
                    break
            
            records.append({
                'date': date_str,
                'description': description,
                'amount': amount,
                'balance': balance,
                'reference': reference
            })
        except Exception as e:
            continue
    
    return records


# ============================================================================
# UPLOAD ENDPOINT
# ============================================================================
@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    bank: str = Form(...),
    currency: str = Form(...)
):
    """Upload bank statement for specific bank and currency"""
    _require_db()
    
    if bank not in BANKS:
        raise HTTPException(status_code=400, detail=f"Geçersiz banka. Desteklenen: {BANKS}")
    if currency not in CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Geçersiz para birimi. Desteklenen: {CURRENCIES}")
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyası (.xlsx, .xls)")
    
    try:
        contents = await file.read()
        # Try multiple engines for compatibility
        df = None
        errors = []
        
        # For .xlsx files, try calamine first (handles problematic xlsx), then openpyxl
        if file.filename.endswith('.xlsx'):
            for engine in ['calamine', 'openpyxl']:
                try:
                    df = pd.read_excel(io.BytesIO(contents), engine=engine)
                    break
                except Exception as e:
                    errors.append(f"{engine}: {str(e)[:50]}")
        else:
            # For .xls files, use xlrd
            try:
                df = pd.read_excel(io.BytesIO(contents), engine='xlrd')
            except Exception as e:
                errors.append(f"xlrd: {str(e)[:50]}")
        
        if df is None:
            raise HTTPException(status_code=400, detail=f"Excel okuma hatası: {'; '.join(errors)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel okuma hatası: {str(e)}")
    
    # Parse records
    records = parse_bank_statement(df)
    
    if not records:
        raise HTTPException(status_code=400, detail="İşlem bulunamadı")
    
    # Check for duplicates (reference + amount combination)
    existing = await _db.real_costs_transactions.find(
        {"bank": bank, "currency": currency},
        {"reference": 1, "amount": 1}
    ).to_list(50000)
    existing_keys = {f"{t.get('reference')}_{t.get('amount')}" for t in existing if t.get("reference")}
    
    # Create upload record
    upload_id = str(uuid4())
    now = datetime.now(timezone.utc)
    
    # Save original file
    file_ext = Path(file.filename).suffix
    stored_filename = f"{upload_id}{file_ext}"
    file_path = UPLOAD_DIR / stored_filename
    
    # Reset file position and save
    await file.seek(0)
    file_content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Process records
    records_to_insert = []
    skipped = 0
    last_balance = None
    
    for record in records:
        ref = record.get('reference', '').strip()
        amount = record.get('amount', 0)
        unique_key = f"{ref}_{amount}"
        
        if ref and unique_key in existing_keys:
            skipped += 1
            continue
        if ref:
            existing_keys.add(unique_key)
        
        parsed_date = parse_date(record['date'])
        if parsed_date:
            month = parsed_date.strftime("%Y-%m")
            year = parsed_date.strftime("%Y")
        else:
            month = now.strftime("%Y-%m")
            year = now.strftime("%Y")
        
        # Track last balance (for final balance)
        if record.get('balance') is not None:
            last_balance = record['balance']
        
        doc = {
            "id": str(uuid4()),
            "upload_id": upload_id,
            "bank": bank,
            "currency": currency,
            "month": month,
            "year": year,
            "date": record['date'],
            "parsed_date": parsed_date.isoformat() if parsed_date else None,
            "description": record['description'],
            "amount": amount,
            "balance": record.get('balance'),
            "reference": ref,
            "created_at": now.isoformat()
        }
        records_to_insert.append(doc)
    
    # Save upload record
    upload_month = now.strftime("%Y-%m")
    upload_doc = {
        "id": upload_id,
        "filename": file.filename,
        "stored_filename": stored_filename,
        "bank": bank,
        "currency": currency,
        "record_count": len(records_to_insert),
        "skipped_duplicates": skipped,
        "last_balance": last_balance,
        "upload_month": upload_month,
        "uploaded_at": now.isoformat()
    }
    await _db.real_costs_uploads.insert_one(upload_doc)
    
    # Save transactions
    if records_to_insert:
        await _db.real_costs_transactions.insert_many(records_to_insert)
    
    return {
        "ok": True,
        "upload_id": upload_id,
        "bank": bank,
        "currency": currency,
        "record_count": len(records_to_insert),
        "skipped": skipped,
        "last_balance": last_balance,
        "message": f"{len(records_to_insert)} işlem yüklendi ({bank} {currency})"
    }


# ============================================================================
# SUMMARY - Main Dashboard Data
# ============================================================================
@router.get("/summary")
async def get_summary():
    """
    Get summary grouped by bank and currency.
    Shows current balance for each bank/currency combination.
    """
    _require_db()
    
    # Get opening balances
    opening_balances = await _db.real_costs_opening.find({}, {"_id": 0}).to_list(100)
    opening_map = {f"{b['bank']}_{b['currency']}": b.get("amount", 0) for b in opening_balances}
    
    # Get net movements per bank/currency
    pipeline = [
        {"$group": {
            "_id": {"bank": "$bank", "currency": "$currency"},
            "net_movement": {"$sum": "$amount"},
            "transaction_count": {"$sum": 1}
        }}
    ]
    movements = await _db.real_costs_transactions.aggregate(pipeline).to_list(100)
    
    # Get last balance from most recent transaction per bank/currency
    last_balance_pipeline = [
        {"$sort": {"parsed_date": -1}},
        {"$group": {
            "_id": {"bank": "$bank", "currency": "$currency"},
            "last_balance": {"$first": "$balance"},
            "last_date": {"$first": "$date"}
        }}
    ]
    last_balances = await _db.real_costs_transactions.aggregate(last_balance_pipeline).to_list(100)
    last_balance_map = {
        f"{lb['_id']['bank']}_{lb['_id']['currency']}": {
            "balance": lb.get("last_balance"),
            "date": lb.get("last_date")
        }
        for lb in last_balances
    }
    
    # Build result
    result = {
        "banks": {}
    }
    
    for bank in BANKS:
        result["banks"][bank] = {}
        for currency in CURRENCIES:
            key = f"{bank}_{currency}"
            opening = opening_map.get(key, 0)
            
            # Find movement for this bank/currency
            movement_data = next(
                (m for m in movements if m["_id"]["bank"] == bank and m["_id"]["currency"] == currency),
                None
            )
            net_movement = movement_data["net_movement"] if movement_data else 0
            tx_count = movement_data["transaction_count"] if movement_data else 0
            
            # Get last balance from Excel (most accurate)
            last_data = last_balance_map.get(key, {})
            excel_balance = last_data.get("balance")
            last_date = last_data.get("date")
            
            # Current balance: prefer Excel's last balance, else calculate
            if excel_balance is not None:
                current_balance = excel_balance
            else:
                current_balance = opening + net_movement
            
            result["banks"][bank][currency] = {
                "opening": opening,
                "net_movement": net_movement,
                "current_balance": current_balance,
                "last_date": last_date,
                "transaction_count": tx_count
            }
    
    return result


# ============================================================================
# MONTHLY OVERVIEW - For Home Dashboard
# ============================================================================
@router.get("/monthly-overview")
async def get_monthly_overview():
    """Get current month overview for home dashboard"""
    _require_db()
    
    from datetime import datetime
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    
    # Get current month transactions
    pipeline = [
        {"$match": {"month": current_month}},
        {"$group": {
            "_id": None,
            "income": {"$sum": {"$cond": [{"$gt": ["$amount", 0]}, "$amount", 0]}},
            "expense": {"$sum": {"$cond": [{"$lt": ["$amount", 0]}, {"$abs": "$amount"}, 0]}},
            "net": {"$sum": "$amount"},
            "count": {"$sum": 1}
        }}
    ]
    
    result = await _db.real_costs_transactions.aggregate(pipeline).to_list(1)
    
    if result:
        data = result[0]
        return {
            "months": [{
                "month": current_month,
                "income": data.get("income", 0),
                "expense": data.get("expense", 0),
                "net": data.get("net", 0),
                "count": data.get("count", 0)
            }]
        }
    
    return {
        "months": [{
            "month": current_month,
            "income": 0,
            "expense": 0,
            "net": 0,
            "count": 0
        }]
    }


# ============================================================================
# MONTHS - Grouped by Year
# ============================================================================
@router.get("/months")
async def get_months():
    """Get monthly breakdown grouped by year, then by bank/currency"""
    _require_db()
    
    pipeline = [
        {"$group": {
            "_id": {
                "year": "$year",
                "month": "$month",
                "bank": "$bank",
                "currency": "$currency"
            },
            "income": {"$sum": {"$cond": [{"$gt": ["$amount", 0]}, "$amount", 0]}},
            "expense": {"$sum": {"$cond": [{"$lt": ["$amount", 0]}, {"$abs": "$amount"}, 0]}},
            "net": {"$sum": "$amount"},
            "count": {"$sum": 1},
            "last_balance": {"$last": "$balance"}
        }},
        {"$sort": {"_id.month": -1}}
    ]
    
    raw_data = await _db.real_costs_transactions.aggregate(pipeline).to_list(500)
    
    # Group by year
    years = {}
    for item in raw_data:
        year = item["_id"]["year"]
        month = item["_id"]["month"]
        bank = item["_id"]["bank"]
        currency = item["_id"]["currency"]
        
        if year not in years:
            years[year] = {}
        if month not in years[year]:
            years[year][month] = {}
        
        key = f"{bank}_{currency}"
        years[year][month][key] = {
            "bank": bank,
            "currency": currency,
            "income": item["income"],
            "expense": item["expense"],
            "net": item["net"],
            "count": item["count"],
            "last_balance": item.get("last_balance")
        }
    
    # Sort years descending, months descending within each year
    result = []
    for year in sorted(years.keys(), reverse=True):
        year_data = {
            "year": year,
            "months": []
        }
        for month in sorted(years[year].keys(), reverse=True):
            year_data["months"].append({
                "month": month,
                "data": years[year][month]
            })
        result.append(year_data)
    
    return result


# ============================================================================
# MONTH DETAIL
# ============================================================================
@router.get("/month/{month}")
async def get_month_detail(month: str, bank: Optional[str] = None, currency: Optional[str] = None):
    """Get detailed transactions for a specific month"""
    _require_db()
    
    query = {"month": month}
    if bank:
        query["bank"] = bank
    if currency:
        query["currency"] = currency
    
    transactions = await _db.real_costs_transactions.find(
        query, {"_id": 0}
    ).sort("parsed_date", -1).to_list(1000)
    
    return {
        "month": month,
        "transactions": transactions
    }


# ============================================================================
# UPLOADS - Grouped by Month
# ============================================================================
@router.get("/uploads")
async def get_uploads():
    """Get all uploads grouped by month, sorted by date descending"""
    _require_db()
    
    uploads = await _db.real_costs_uploads.find({}, {"_id": 0}).sort("uploaded_at", -1).to_list(500)
    
    # Group by upload month
    months = {}
    for u in uploads:
        month = u.get("upload_month", "unknown")
        if month not in months:
            months[month] = []
        months[month].append(u)
    
    # Convert to sorted list
    result = []
    for month in sorted(months.keys(), reverse=True):
        result.append({
            "month": month,
            "uploads": months[month]
        })
    
    return result


# ============================================================================
# DOWNLOAD ORIGINAL FILE
# ============================================================================
@router.get("/uploads/{upload_id}/download")
async def download_upload(upload_id: str):
    """Download original Excel file"""
    _require_db()
    
    upload = await _db.real_costs_uploads.find_one({"id": upload_id}, {"_id": 0})
    if not upload:
        raise HTTPException(status_code=404, detail="Upload bulunamadı")
    
    stored_filename = upload.get("stored_filename")
    if not stored_filename:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    file_path = UPLOAD_DIR / stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
    return FileResponse(
        path=str(file_path),
        filename=upload.get("filename", stored_filename),
        media_type="application/vnd.ms-excel"
    )


# ============================================================================
# DELETE UPLOAD
# ============================================================================
@router.delete("/uploads/{upload_id}")
async def delete_upload(upload_id: str):
    """Delete upload and all related transactions"""
    _require_db()
    
    # Get upload info
    upload = await _db.real_costs_uploads.find_one({"id": upload_id})
    if not upload:
        raise HTTPException(status_code=404, detail="Upload bulunamadı")
    
    # Delete file
    stored_filename = upload.get("stored_filename")
    if stored_filename:
        file_path = UPLOAD_DIR / stored_filename
        if file_path.exists():
            file_path.unlink()
    
    # Delete transactions
    await _db.real_costs_transactions.delete_many({"upload_id": upload_id})
    
    # Delete upload record
    await _db.real_costs_uploads.delete_one({"id": upload_id})
    
    return {"ok": True, "message": "Upload ve işlemler silindi"}
