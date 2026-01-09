# server.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import List, Optional
import os
import uuid
from pathlib import Path
import shutil
import asyncio

from playwright.async_api import async_playwright

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from warehouse_routes import router as warehouse_router, init_warehouse_db
from inventory_routes import router as inventory_router, set_database as set_inventory_db
from real_costs_routes import router as real_costs_router, set_db as set_real_costs_db
from sofis_import_routes import router as sofis_router, set_database as set_sofis_db

from models import (
    Customer, CustomerCreate, CustomerUpdate,
    Product, ProductCreate, ProductUpdate,
    Quotation, QuotationCreate, QuotationUpdate,
    LineItemCreate,
    CostCategory, CostCategoryCreate,
    InternalCost, InternalCostCreate,
    Representative, RepresentativeCreate, RepresentativeUpdate
)

# ============================
# FastAPI
# ============================
app = FastAPI(title="Quotation Management API")
api_router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# MongoDB
# ============================
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.quotation_db

# ✅ Warehouse / Inventory / RealCosts / Sofis aynı DB’yi kullanacak
init_warehouse_db(db)
set_inventory_db(db)
set_real_costs_db(db)
set_sofis_db(db)

# Routers
api_router.include_router(warehouse_router, prefix="/warehouse", tags=["warehouse"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(real_costs_router, prefix="/real-costs", tags=["real-costs"])
api_router.include_router(sofis_router, prefix="/sofis", tags=["sofis"])

# ============================
# Helpers
# ============================
async def generate_quote_no(quotation_type: str, revision_no: int = 0) -> tuple:
    """Generate quotation number based on total count: Q-YYMMDD-XXX"""
    now = datetime.now()
    date_part = now.strftime("%y%m%d")

    total_count = await db.quotations.count_documents({})
    counter = total_count + 1

    base_quote_no = f"Q-{date_part}-{counter:03d}"

    if revision_no == 0:
        quote_no = base_quote_no
    else:
        quote_no = f"{base_quote_no}-R{revision_no}"

    return quote_no, base_quote_no


def calculate_line_totals(line_item: dict) -> dict:
    quantity = float(line_item.get("quantity", 0) or 0)
    unit_price = float(line_item.get("unit_price", 0) or 0)

    line_item["subtotal_before_discount"] = quantity * unit_price
    line_item["discount_amount"] = 0
    line_item["line_total"] = quantity * unit_price
    return line_item


def calculate_totals_by_currency(line_items: List[dict]) -> dict:
    totals = {}
    for item in line_items:
        if item.get("is_optional", False):
            continue
        currency = item.get("currency", "EUR")
        line_total = float(item.get("line_total", 0) or 0)
        totals[currency] = totals.get(currency, 0) + line_total
    return {"totals": totals}


def format_currency(amount: float, currency: str) -> str:
    try:
        return f"{float(amount):,.2f} {currency}".replace(",", " ")
    except Exception:
        return f"{amount} {currency}"


def build_native_quotation_pdf(quotation: dict, pdf_path: str) -> None:
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=f"Teklif {quotation.get('quote_no', '')}",
    )
    styles = getSampleStyleSheet()
    elements = []

    title = quotation.get("subject") or "Teklif"
    elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    customer_name = quotation.get("customer_name") or "-"
    quote_no = quotation.get("quote_no") or "-"
    date_value = quotation.get("date")
    if isinstance(date_value, datetime):
        date_text = date_value.strftime("%d.%m.%Y")
    else:
        date_text = str(date_value) if date_value else "-"

    meta_lines = [
        f"<b>Teklif No:</b> {quote_no}",
        f"<b>Müşteri:</b> {customer_name}",
        f"<b>Tarih:</b> {date_text}",
        f"<b>Proje Kodu:</b> {quotation.get('project_code') or '-'}",
    ]
    for line in meta_lines:
        elements.append(Paragraph(line, styles["Normal"]))
    elements.append(Spacer(1, 16))

    line_items = quotation.get("line_items", []) or []
    if line_items:
        table_data = [["#", "Kalem", "Adet", "Birim", "Birim Fiyat", "Toplam"]]
        totals_by_currency = {}

        idx_counter = 0
        for item in line_items:
            if item.get("is_optional"):
                continue
            idx_counter += 1
            currency = item.get("currency") or "EUR"
            quantity = float(item.get("quantity") or 0)
            unit = item.get("unit") or ""
            unit_price = float(item.get("unit_price") or 0)
            line_total = item.get("line_total")
            if line_total is None:
                line_total = quantity * unit_price
            line_total = float(line_total or 0)

            totals_by_currency[currency] = totals_by_currency.get(currency, 0) + line_total

            table_data.append([
                str(idx_counter),
                item.get("item_short_name") or "-",
                f"{quantity:g}",
                unit,
                format_currency(unit_price, currency),
                format_currency(line_total, currency),
            ])

        table = Table(table_data, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004aad")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 16))

        totals_rows = [["Toplamlar", ""]]
        for currency, total in totals_by_currency.items():
            totals_rows.append([currency, format_currency(total, currency)])
        totals_table = Table(totals_rows, colWidths=[120, 120], hAlign="RIGHT")
        totals_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004aad")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(totals_table)
    else:
        elements.append(Paragraph("Kalem bulunamadı.", styles["Normal"]))

    notes = quotation.get("notes")
    if notes:
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("<b>Notlar</b>", styles["Heading3"]))
        elements.append(Paragraph(notes, styles["BodyText"]))

    doc.build(elements)


def _dt_from_iso(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return value
    return value


def _sanitize_filename(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("/", "-").replace("\\", "-")
    s = s.replace("\n", " ").replace("\r", " ")
    return s


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_dict = customer.model_dump()
    customer_dict["id"] = str(uuid.uuid4())
    customer_dict["is_active"] = True
    customer_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    customer_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.customers.insert_one(customer_dict)
    created = await db.customers.find_one({"id": customer_dict["id"]}, {"_id": 0})

    created["created_at"] = _dt_from_iso(created.get("created_at"))
    created["updated_at"] = _dt_from_iso(created.get("updated_at"))
    return created


@api_router.get("/customers", response_model=List[Customer])
async def get_customers(is_active: bool = None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    customers = await db.customers.find(query, {"_id": 0}).to_list(1000)
    for c in customers:
        c["created_at"] = _dt_from_iso(c.get("created_at"))
        c["updated_at"] = _dt_from_iso(c.get("updated_at"))
    return customers


@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer["created_at"] = _dt_from_iso(customer.get("created_at"))
    customer["updated_at"] = _dt_from_iso(customer.get("updated_at"))
    return customer


@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer: CustomerUpdate):
    existing = await db.customers.find_one({"id": customer_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_dict = {k: v for k, v in customer.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.customers.update_one({"id": customer_id}, {"$set": update_dict})
    updated = await db.customers.find_one({"id": customer_id}, {"_id": 0})

    updated["created_at"] = _dt_from_iso(updated.get("created_at"))
    updated["updated_at"] = _dt_from_iso(updated.get("updated_at"))
    return updated


@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    result = await db.customers.update_one(
        {"id": customer_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deactivated", "id": customer_id}


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================
@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    product_dict = product.model_dump()
    product_dict["id"] = str(uuid.uuid4())
    product_dict["is_active"] = True
    product_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    product_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.products.insert_one(product_dict)
    created = await db.products.find_one({"id": product_dict["id"]}, {"_id": 0})

    created["created_at"] = _dt_from_iso(created.get("created_at"))
    created["updated_at"] = _dt_from_iso(created.get("updated_at"))
    return created


@api_router.get("/products", response_model=List[Product])
async def get_products(product_type: str = None, is_active: bool = None):
    query = {}
    if product_type:
        query["product_type"] = product_type
    if is_active is not None:
        query["is_active"] = is_active

    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    for p in products:
        p["created_at"] = _dt_from_iso(p.get("created_at"))
        p["updated_at"] = _dt_from_iso(p.get("updated_at"))
    return products


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product["created_at"] = _dt_from_iso(product.get("created_at"))
    product["updated_at"] = _dt_from_iso(product.get("updated_at"))
    return product


@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductUpdate):
    existing = await db.products.find_one({"id": product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    update_dict = {k: v for k, v in product.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.products.update_one({"id": product_id}, {"$set": update_dict})
    updated = await db.products.find_one({"id": product_id}, {"_id": 0})

    updated["created_at"] = _dt_from_iso(updated.get("created_at"))
    updated["updated_at"] = _dt_from_iso(updated.get("updated_at"))
    return updated


@api_router.delete("/products/delete-all")
async def delete_all_products(product_type: str = None, confirm: str = None):
    """
    Delete all products. Requires confirm=yes parameter for safety.
    Optional product_type filter: 'sales' or 'service'
    """
    if confirm != "yes":
        raise HTTPException(status_code=400, detail="Silme işlemi için confirm=yes parametresi gerekli")

    query = {}
    if product_type:
        query["product_type"] = product_type

    result = await db.products.delete_many(query)

    if not product_type:
        await db.product_groups.delete_many({})
        return {"message": f"{result.deleted_count} ürün ve tüm gruplar silindi"}

    return {"message": f"{result.deleted_count} ürün silindi"}


@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product permanently"""
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}


@api_router.get("/products/{product_id}/price-history")
async def get_product_price_history(product_id: str, limit: int = 5):
    """
    Get price history for a product from previous quotations.
    Returns last N quotations where this product was used, with customer name and price.
    """
    pipeline = [
        {"$match": {"line_items.product_id": product_id}},
        {"$sort": {"created_at": -1}},
        {"$limit": limit * 2},
        {"$project": {
            "_id": 0,
            "id": 1,
            "quotation_number": 1,
            "customer_id": 1,
            "created_at": 1,
            "line_items": {
                "$filter": {
                    "input": "$line_items",
                    "as": "item",
                    "cond": {"$eq": ["$$item.product_id", product_id]}
                }
            }
        }}
    ]

    quotations = await db.quotations.aggregate(pipeline).to_list(limit * 2)

    customer_ids = list(set(q.get("customer_id") for q in quotations if q.get("customer_id")))
    customers = await db.customers.find(
        {"id": {"$in": customer_ids}},
        {"_id": 0, "id": 1, "name": 1}
    ).to_list(100)
    customer_map = {c["id"]: c["name"] for c in customers}

    history = []
    for q in quotations:
        for item in q.get("line_items", []):
            history.append({
                "quotation_id": q.get("id"),
                "quotation_number": q.get("quotation_number", ""),
                "customer_name": customer_map.get(q.get("customer_id"), "Bilinmiyor"),
                "date": q.get("created_at", ""),
                "unit_price": item.get("unit_price", 0),
                "currency": item.get("currency", "EUR"),
                "quantity": item.get("quantity", 1),
                "variant_name": item.get("variant_name", ""),
                "item_name": item.get("item_short_name", "")
            })

    history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)[:limit]
    return {"history": history, "total": len(history)}


# ============================================================================
# PRODUCT GROUPS ENDPOINTS
# ============================================================================
@api_router.get("/product-groups")
async def get_product_groups():
    groups = await db.product_groups.find({}, {"_id": 0}).sort("sort_order", 1).to_list(100)
    return groups


@api_router.post("/product-groups")
async def create_product_group(data: dict):
    group_dict = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", "Yeni Grup"),
        "description": data.get("description", ""),
        "sort_order": data.get("sort_order", 999),
        "is_expanded": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.product_groups.insert_one(group_dict)
    return {"ok": True, "group": {k: v for k, v in group_dict.items() if k != "_id"}}


@api_router.put("/product-groups/{group_id}")
async def update_product_group(group_id: str, data: dict):
    existing = await db.product_groups.find_one({"id": group_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Group not found")

    update_data = {}
    if "name" in data:
        update_data["name"] = data["name"]
    if "description" in data:
        update_data["description"] = data["description"]
    if "sort_order" in data:
        update_data["sort_order"] = data["sort_order"]
    if "is_expanded" in data:
        update_data["is_expanded"] = data["is_expanded"]

    if update_data:
        await db.product_groups.update_one({"id": group_id}, {"$set": update_data})

    updated = await db.product_groups.find_one({"id": group_id}, {"_id": 0})
    return {"ok": True, "group": updated}


@api_router.delete("/product-groups/{group_id}")
async def delete_product_group(group_id: str):
    await db.products.update_many({"group_id": group_id}, {"$set": {"group_id": None}})
    result = await db.product_groups.delete_one({"id": group_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"ok": True, "message": "Grup silindi"}


@api_router.put("/products/{product_id}/group")
async def assign_product_to_group(product_id: str, data: dict):
    group_id = data.get("group_id")

    existing = await db.products.find_one({"id": product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.products.update_one({"id": product_id}, {"$set": {"group_id": group_id}})
    return {"ok": True, "message": "Ürün grubu güncellendi"}


@api_router.put("/products/bulk-assign-group")
async def bulk_assign_products_to_group(data: dict):
    product_ids = data.get("product_ids", [])
    group_id = data.get("group_id")

    if not product_ids:
        raise HTTPException(status_code=400, detail="No products specified")

    result = await db.products.update_many(
        {"id": {"$in": product_ids}},
        {"$set": {"group_id": group_id}}
    )
    return {"ok": True, "modified_count": result.modified_count}


# ============================================================================
# REPRESENTATIVE ENDPOINTS
# ============================================================================
@api_router.post("/representatives", response_model=Representative)
async def create_representative(representative: RepresentativeCreate):
    rep_dict = representative.model_dump()
    rep_dict["id"] = str(uuid.uuid4())
    rep_dict["is_active"] = True
    rep_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    rep_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.representatives.insert_one(rep_dict)
    created = await db.representatives.find_one({"id": rep_dict["id"]}, {"_id": 0})

    created["created_at"] = _dt_from_iso(created.get("created_at"))
    created["updated_at"] = _dt_from_iso(created.get("updated_at"))
    return created


@api_router.get("/representatives", response_model=List[Representative])
async def get_representatives(is_active: bool = None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    reps = await db.representatives.find(query, {"_id": 0}).to_list(1000)
    for r in reps:
        r["created_at"] = _dt_from_iso(r.get("created_at"))
        r["updated_at"] = _dt_from_iso(r.get("updated_at"))
    return reps


@api_router.put("/representatives/{rep_id}", response_model=Representative)
async def update_representative(rep_id: str, representative: RepresentativeUpdate):
    existing = await db.representatives.find_one({"id": rep_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Representative not found")

    update_dict = {k: v for k, v in representative.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.representatives.update_one({"id": rep_id}, {"$set": update_dict})
    updated = await db.representatives.find_one({"id": rep_id}, {"_id": 0})

    updated["created_at"] = _dt_from_iso(updated.get("created_at"))
    updated["updated_at"] = _dt_from_iso(updated.get("updated_at"))
    return updated


# ============================================================================
# QUOTATION ENDPOINTS
# ============================================================================
@api_router.patch("/quotations/{quotation_id}/status")
async def update_quotation_status(quotation_id: str, payload: dict):
    existing = await db.quotations.find_one({"id": quotation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Quotation not found")

    offer_status = (payload.get("offer_status") or "").lower().strip()
    rejection_reason = (payload.get("rejection_reason") or "").strip()

    if offer_status not in ["pending", "accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid offer_status")

    update = {
        "offer_status": offer_status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if offer_status == "rejected":
        update["rejection_reason"] = rejection_reason
    else:
        update["rejection_reason"] = None

    previous_status = existing.get("offer_status", "pending")

    await db.quotations.update_one({"id": quotation_id}, {"$set": update})
    updated = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})

    # Reservations
    if offer_status == "accepted" and previous_status != "accepted":
        line_items = existing.get("line_items", [])
        for item in line_items:
            if item.get("is_optional"):
                continue
            product_id = item.get("product_id")
            variant_id = item.get("variant_id") or item.get("model_name") or ""
            quantity = float(item.get("quantity", 0) or 0)

            if product_id and quantity > 0:
                stock_items = await db.stock_items.find({"product_id": product_id}).to_list(100)
                remaining_qty = quantity

                for stock_item in stock_items:
                    if remaining_qty <= 0:
                        break
                    current_reserved = float(stock_item.get("reserved_quantity", 0) or 0)
                    available = float(stock_item.get("quantity", 0) or 0) - current_reserved
                    reserve_qty = min(remaining_qty, max(0, available))

                    if reserve_qty > 0:
                        await db.stock_items.update_one(
                            {"id": stock_item["id"]},
                            {"$set": {"reserved_quantity": current_reserved + reserve_qty}}
                        )
                        remaining_qty -= reserve_qty

    elif previous_status == "accepted" and offer_status != "accepted":
        line_items = existing.get("line_items", [])
        for item in line_items:
            if item.get("is_optional"):
                continue
            product_id = item.get("product_id")
            quantity = float(item.get("quantity", 0) or 0)

            if product_id and quantity > 0:
                stock_items = await db.stock_items.find({"product_id": product_id}).to_list(100)
                remaining_qty = quantity

                for stock_item in stock_items:
                    if remaining_qty <= 0:
                        break
                    current_reserved = float(stock_item.get("reserved_quantity", 0) or 0)
                    release_qty = min(remaining_qty, current_reserved)

                    if release_qty > 0:
                        await db.stock_items.update_one(
                            {"id": stock_item["id"]},
                            {"$set": {"reserved_quantity": max(0, current_reserved - release_qty)}}
                        )
                        remaining_qty -= release_qty

    return updated


@api_router.post("/quotations/{quotation_id}/deliver")
async def deliver_quotation(quotation_id: str):
    existing = await db.quotations.find_one({"id": quotation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")

    if existing.get("offer_status") != "accepted":
        raise HTTPException(status_code=400, detail="Sadece onaylanmış teklifler teslim edilebilir")

    if existing.get("delivery_status") == "delivered":
        raise HTTPException(status_code=400, detail="Bu teklif zaten teslim edilmiş")

    line_items = existing.get("line_items", [])
    stock_decreased = []

    for item in line_items:
        if item.get("is_optional"):
            continue

        product_id = item.get("product_id")
        variant_id = item.get("variant_id") or item.get("model_name") or ""
        quantity = float(item.get("quantity", 0) or 0)

        if not product_id or quantity <= 0:
            continue

        stock_items = await db.stock_items.find({"product_id": product_id}).to_list(100)

        remaining_qty = quantity
        for stock_item in stock_items:
            if remaining_qty <= 0:
                break

            current_qty = float(stock_item.get("quantity", 0) or 0)
            current_reserved = float(stock_item.get("reserved_quantity", 0) or 0)
            decrease_qty = min(remaining_qty, current_qty)

            if decrease_qty > 0:
                new_qty = max(0, current_qty - decrease_qty)
                new_reserved = max(0, current_reserved - decrease_qty)

                await db.stock_items.update_one(
                    {"id": stock_item["id"]},
                    {"$set": {"quantity": new_qty, "reserved_quantity": new_reserved}}
                )

                stock_decreased.append({
                    "product_id": product_id,
                    "variant_id": variant_id,
                    "decreased": decrease_qty
                })

                remaining_qty -= decrease_qty

    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {
            "delivery_status": "delivered",
            "delivered_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"ok": True, "message": "Teslimat tamamlandı", "stock_decreased": stock_decreased}


@api_router.post("/quotations/{quotation_id}/revert-delivery")
async def revert_delivery(quotation_id: str):
    existing = await db.quotations.find_one({"id": quotation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")

    if existing.get("delivery_status") != "delivered":
        raise HTTPException(status_code=400, detail="Bu teklif teslim edilmemiş")

    line_items = existing.get("line_items", [])
    stock_restored = []

    for item in line_items:
        if item.get("is_optional"):
            continue

        product_id = item.get("product_id")
        variant_id = item.get("variant_id") or item.get("model_name") or ""
        quantity = float(item.get("quantity", 0) or 0)

        if not product_id or quantity <= 0:
            continue

        stock_items = await db.stock_items.find({"product_id": product_id}).to_list(100)
        if stock_items:
            stock_item = stock_items[0]
            current_qty = float(stock_item.get("quantity", 0) or 0)
            current_reserved = float(stock_item.get("reserved_quantity", 0) or 0)

            await db.stock_items.update_one(
                {"id": stock_item["id"]},
                {"$set": {
                    "quantity": current_qty + quantity,
                    "reserved_quantity": current_reserved + quantity
                }}
            )

            stock_restored.append({
                "product_id": product_id,
                "variant_id": variant_id,
                "restored": quantity
            })

    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {
            "delivery_status": "pending",
            "delivered_at": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"ok": True, "message": "Teslimat geri alındı, stoklar yeniden eklendi", "stock_restored": stoc_
