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

# ✅ Warehouse aynı DB’yi kullanacak
init_warehouse_db(db)
# ✅ Inventory aynı DB'yi kullanacak
set_inventory_db(db)
# ✅ Real Costs aynı DB'yi kullanacak
set_real_costs_db(db)
# ✅ SOFIS Import aynı DB'yi kullanacak
set_sofis_db(db)
# ✅ SOFIS Import aynı DB'yi kullanacak
set_sofis_db(db)

# ✅ Warehouse router’ı /api/warehouse altına al
api_router.include_router(
    warehouse_router,
    prefix="/warehouse",
    tags=["warehouse"]
)

# ✅ Inventory router'ı /api/inventory altına al
api_router.include_router(
    inventory_router,
    prefix="/inventory",
    tags=["inventory"]
)

# ✅ Real Costs router'ı /api/real-costs altına al
api_router.include_router(
    real_costs_router,
    prefix="/real-costs",
    tags=["real-costs"]
)

# ✅ SOFIS Import router'ı /api/sofis altına al
api_router.include_router(
    sofis_router,
    prefix="/sofis",
    tags=["sofis"]
)

# ✅ SOFIS Import router'ı /api/sofis altına al
api_router.include_router(
    sofis_router,
    prefix="/sofis",
    tags=["sofis"]
)

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
    quantity = line_item.get("quantity", 0)
    unit_price = line_item.get("unit_price", 0)

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
        line_total = item.get("line_total", 0)
        totals[currency] = totals.get(currency, 0) + line_total
    return {"totals": totals}

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

    if isinstance(created["created_at"], str):
        created["created_at"] = datetime.fromisoformat(created["created_at"])
    if isinstance(created["updated_at"], str):
        created["updated_at"] = datetime.fromisoformat(created["updated_at"])
    return created


@api_router.get("/customers", response_model=List[Customer])
async def get_customers(is_active: bool = None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    customers = await db.customers.find(query, {"_id": 0}).to_list(1000)
    for c in customers:
        if isinstance(c["created_at"], str):
            c["created_at"] = datetime.fromisoformat(c["created_at"])
        if isinstance(c["updated_at"], str):
            c["updated_at"] = datetime.fromisoformat(c["updated_at"])
    return customers


@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if isinstance(customer["created_at"], str):
        customer["created_at"] = datetime.fromisoformat(customer["created_at"])
    if isinstance(customer["updated_at"], str):
        customer["updated_at"] = datetime.fromisoformat(customer["updated_at"])
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

    if isinstance(updated["created_at"], str):
        updated["created_at"] = datetime.fromisoformat(updated["created_at"])
    if isinstance(updated["updated_at"], str):
        updated["updated_at"] = datetime.fromisoformat(updated["updated_at"])
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

    if isinstance(created["created_at"], str):
        created["created_at"] = datetime.fromisoformat(created["created_at"])
    if isinstance(created["updated_at"], str):
        created["updated_at"] = datetime.fromisoformat(created["updated_at"])
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
        if isinstance(p["created_at"], str):
            p["created_at"] = datetime.fromisoformat(p["created_at"])
        if isinstance(p["updated_at"], str):
            p["updated_at"] = datetime.fromisoformat(p["updated_at"])
    return products


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if isinstance(product["created_at"], str):
        product["created_at"] = datetime.fromisoformat(product["created_at"])
    if isinstance(product["updated_at"], str):
        product["updated_at"] = datetime.fromisoformat(product["updated_at"])
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

    if isinstance(updated["created_at"], str):
        updated["created_at"] = datetime.fromisoformat(updated["created_at"])
    if isinstance(updated["updated_at"], str):
        updated["updated_at"] = datetime.fromisoformat(updated["updated_at"])
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
    
    # Also delete related groups if deleting all
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
    # Find quotations containing this product in line_items
    pipeline = [
        {"$match": {"line_items.product_id": product_id}},
        {"$sort": {"created_at": -1}},
        {"$limit": limit * 2},  # Get more in case of duplicates
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
    
    # Get customer names
    customer_ids = list(set(q.get("customer_id") for q in quotations if q.get("customer_id")))
    customers = await db.customers.find(
        {"id": {"$in": customer_ids}}, 
        {"_id": 0, "id": 1, "name": 1}
    ).to_list(100)
    customer_map = {c["id"]: c["name"] for c in customers}
    
    # Build result
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
    
    # Sort by date and limit
    history = sorted(history, key=lambda x: x.get("date", ""), reverse=True)[:limit]
    
    return {"history": history, "total": len(history)}


# ============================================================================
# PRODUCT GROUPS ENDPOINTS
# ============================================================================
@api_router.get("/product-groups")
async def get_product_groups():
    """Get all product groups"""
    groups = await db.product_groups.find({}, {"_id": 0}).sort("sort_order", 1).to_list(100)
    return groups


@api_router.post("/product-groups")
async def create_product_group(data: dict):
    """Create a new product group"""
    group_dict = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", "Yeni Grup"),
        "description": data.get("description", ""),
        "sort_order": data.get("sort_order", 999),
        "is_expanded": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.product_groups.insert_one(group_dict)
    return {"ok": True, "group": {k: v for k, v in group_dict.items() if k != '_id'}}


@api_router.put("/product-groups/{group_id}")
async def update_product_group(group_id: str, data: dict):
    """Update a product group (name, sort_order, etc.)"""
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
    """Delete a product group (products will be moved to ungrouped)"""
    # Move all products in this group to ungrouped (group_id = null)
    await db.products.update_many({"group_id": group_id}, {"$set": {"group_id": None}})
    
    # Delete the group
    result = await db.product_groups.delete_one({"id": group_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return {"ok": True, "message": "Grup silindi"}


@api_router.put("/products/{product_id}/group")
async def assign_product_to_group(product_id: str, data: dict):
    """Assign a product to a group"""
    group_id = data.get("group_id")  # Can be None to ungroup
    
    # First check if product exists
    existing = await db.products.find_one({"id": product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.products.update_one(
        {"id": product_id},
        {"$set": {"group_id": group_id}}
    )
    
    return {"ok": True, "message": "Ürün grubu güncellendi"}


@api_router.put("/products/bulk-assign-group")
async def bulk_assign_products_to_group(data: dict):
    """Assign multiple products to a group at once"""
    product_ids = data.get("product_ids", [])
    group_id = data.get("group_id")  # Can be None to ungroup
    
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

    if isinstance(created["created_at"], str):
        created["created_at"] = datetime.fromisoformat(created["created_at"])
    if isinstance(created["updated_at"], str):
        created["updated_at"] = datetime.fromisoformat(created["updated_at"])
    return created


@api_router.get("/representatives", response_model=List[Representative])
async def get_representatives(is_active: bool = None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    reps = await db.representatives.find(query, {"_id": 0}).to_list(1000)
    for r in reps:
        if isinstance(r["created_at"], str):
            r["created_at"] = datetime.fromisoformat(r["created_at"])
        if isinstance(r["updated_at"], str):
            r["updated_at"] = datetime.fromisoformat(r["updated_at"])
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

    if isinstance(updated["created_at"], str):
        updated["created_at"] = datetime.fromisoformat(updated["created_at"])
    if isinstance(updated["updated_at"], str):
        updated["updated_at"] = datetime.fromisoformat(updated["updated_at"])
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

    # Handle stock reservation when status changes
    previous_status = existing.get("offer_status", "pending")
    
    await db.quotations.update_one({"id": quotation_id}, {"$set": update})
    updated = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    
    # If status changed to accepted, create stock reservations
    if offer_status == "accepted" and previous_status != "accepted":
        line_items = existing.get("line_items", [])
        for item in line_items:
            if item.get("is_optional"):
                continue
            product_id = item.get("product_id")
            variant_id = item.get("variant_id") or item.get("model_name") or ""
            quantity = item.get("quantity", 0)
            
            if product_id and quantity > 0:
                # Find matching stock items and add reservation
                stock_items = await db.stock_items.find({
                    "product_id": product_id,
                    "$or": [
                        {"variant_id": variant_id},
                        {"variant_id": None},
                        {"variant_id": ""}
                    ] if not variant_id else [{"variant_id": variant_id}]
                }).to_list(100)
                
                remaining_qty = quantity
                for stock_item in stock_items:
                    if remaining_qty <= 0:
                        break
                    current_reserved = stock_item.get("reserved_quantity", 0)
                    available = stock_item.get("quantity", 0) - current_reserved
                    reserve_qty = min(remaining_qty, available)
                    
                    if reserve_qty > 0:
                        await db.stock_items.update_one(
                            {"id": stock_item["id"]},
                            {"$set": {"reserved_quantity": current_reserved + reserve_qty}}
                        )
                        remaining_qty -= reserve_qty
    
    # If status changed from accepted to something else, release reservations
    elif previous_status == "accepted" and offer_status != "accepted":
        line_items = existing.get("line_items", [])
        for item in line_items:
            if item.get("is_optional"):
                continue
            product_id = item.get("product_id")
            variant_id = item.get("variant_id") or item.get("model_name") or ""
            quantity = item.get("quantity", 0)
            
            if product_id and quantity > 0:
                stock_items = await db.stock_items.find({
                    "product_id": product_id
                }).to_list(100)
                
                remaining_qty = quantity
                for stock_item in stock_items:
                    if remaining_qty <= 0:
                        break
                    current_reserved = stock_item.get("reserved_quantity", 0)
                    release_qty = min(remaining_qty, current_reserved)
                    
                    if release_qty > 0:
                        await db.stock_items.update_one(
                            {"id": stock_item["id"]},
                            {"$set": {"reserved_quantity": max(0, current_reserved - release_qty)}}
                        )
                        remaining_qty -= release_qty
    
    return updated


# Teslimat işlemi - stoktan düşer
@api_router.post("/quotations/{quotation_id}/deliver")
async def deliver_quotation(quotation_id: str):
    """
    Mark quotation as delivered and decrease stock.
    Only works for accepted quotations that haven't been delivered yet.
    """
    existing = await db.quotations.find_one({"id": quotation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")
    
    if existing.get("offer_status") != "accepted":
        raise HTTPException(status_code=400, detail="Sadece onaylanmış teklifler teslim edilebilir")
    
    if existing.get("delivery_status") == "delivered":
        raise HTTPException(status_code=400, detail="Bu teklif zaten teslim edilmiş")
    
    # Get line items and decrease stock
    line_items = existing.get("line_items", [])
    stock_decreased = []
    
    for item in line_items:
        if item.get("is_optional"):
            continue
        
        product_id = item.get("product_id")
        variant_id = item.get("variant_id") or item.get("model_name") or ""
        quantity = item.get("quantity", 0)
        
        if not product_id or quantity <= 0:
            continue
        
        # Find stock items with reservations for this product
        stock_items = await db.stock_items.find({
            "product_id": product_id
        }).to_list(100)
        
        remaining_qty = quantity
        for stock_item in stock_items:
            if remaining_qty <= 0:
                break
            
            current_qty = stock_item.get("quantity", 0)
            current_reserved = stock_item.get("reserved_quantity", 0)
            
            # Calculate how much to decrease
            decrease_qty = min(remaining_qty, current_qty)
            
            if decrease_qty > 0:
                # Decrease quantity and reserved
                new_qty = max(0, current_qty - decrease_qty)
                new_reserved = max(0, current_reserved - decrease_qty)
                
                await db.stock_items.update_one(
                    {"id": stock_item["id"]},
                    {"$set": {
                        "quantity": new_qty,
                        "reserved_quantity": new_reserved
                    }}
                )
                
                stock_decreased.append({
                    "product_id": product_id,
                    "variant_id": variant_id,
                    "decreased": decrease_qty
                })
                
                remaining_qty -= decrease_qty
    
    # Update quotation delivery status
    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {
            "delivery_status": "delivered",
            "delivered_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "ok": True,
        "message": "Teslimat tamamlandı",
        "stock_decreased": stock_decreased
    }


# Teslimatı geri al - stokları geri yükle
@api_router.post("/quotations/{quotation_id}/revert-delivery")
async def revert_delivery(quotation_id: str):
    """
    Revert delivery status and restore stock.
    Only works for delivered quotations.
    """
    existing = await db.quotations.find_one({"id": quotation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")
    
    if existing.get("delivery_status") != "delivered":
        raise HTTPException(status_code=400, detail="Bu teklif teslim edilmemiş")
    
    # Get line items and restore stock
    line_items = existing.get("line_items", [])
    stock_restored = []
    
    for item in line_items:
        if item.get("is_optional"):
            continue
        
        product_id = item.get("product_id")
        variant_id = item.get("variant_id") or item.get("model_name") or ""
        quantity = item.get("quantity", 0)
        
        if not product_id or quantity <= 0:
            continue
        
        # Find stock items for this product
        stock_items = await db.stock_items.find({
            "product_id": product_id
        }).to_list(100)
        
        if stock_items:
            # Add quantity back to first matching stock item
            stock_item = stock_items[0]
            current_qty = stock_item.get("quantity", 0)
            current_reserved = stock_item.get("reserved_quantity", 0)
            
            await db.stock_items.update_one(
                {"id": stock_item["id"]},
                {"$set": {
                    "quantity": current_qty + quantity,
                    "reserved_quantity": current_reserved + quantity  # Also reserve back
                }}
            )
            
            stock_restored.append({
                "product_id": product_id,
                "variant_id": variant_id,
                "restored": quantity
            })
    
    # Update quotation - remove delivery status but keep accepted
    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {
            "delivery_status": "pending",
            "delivered_at": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "ok": True,
        "message": "Teslimat geri alındı, stoklar yeniden eklendi",
        "stock_restored": stock_restored
    }


@api_router.post("/quotations", response_model=Quotation)
async def create_quotation(quotation: QuotationCreate):
    quote_no, base_quote_no = await generate_quote_no(quotation.quotation_type, 0)

    quotation_dict = quotation.model_dump()
    quotation_dict["id"] = str(uuid.uuid4())
    quotation_dict["quote_no"] = quote_no
    quotation_dict["base_quote_no"] = base_quote_no
    quotation_dict["revision_no"] = 0
    quotation_dict["revision_group_id"] = quotation_dict["id"]
    quotation_dict["offer_status"] = "pending"
    quotation_dict["invoice_status"] = "none"
    quotation_dict["is_archived"] = False
    quotation_dict["date"] = datetime.now(timezone.utc).isoformat()
    quotation_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    quotation_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    customer = await db.customers.find_one({"id": quotation.customer_id}, {"_id": 0})
    if customer:
        quotation_dict["customer_name"] = customer.get("name", "")

        contact_person = ""
        contacts = customer.get("contacts", [])
        if contacts:
            primary = next((c for c in contacts if c.get("is_primary")), None)
            contact_person = (primary or contacts[0]).get("name", "")

        quotation_dict["customer_details"] = {
            "contact_person": contact_person,
            "email": customer.get("email"),
            "phone": customer.get("phone"),
            "address": customer.get("address"),
            "city": customer.get("city"),
            "country": customer.get("country"),
        }

    if quotation.representative_id:
        rep = await db.representatives.find_one({"id": quotation.representative_id}, {"_id": 0})
        if rep:
            quotation_dict["representative_name"] = rep.get("name", "")
            quotation_dict["representative_phone"] = rep.get("phone", "")
            quotation_dict["representative_email"] = rep.get("email", "")

    for item in quotation_dict.get("line_items", []):
        item["id"] = str(uuid.uuid4())
        calculate_line_totals(item)

    quotation_dict["totals_by_currency"] = calculate_totals_by_currency(
        quotation_dict.get("line_items", [])
    )

    await db.quotations.insert_one(quotation_dict)
    created = await db.quotations.find_one({"id": quotation_dict["id"]}, {"_id": 0})

    for field in ["date", "created_at", "updated_at"]:
        if isinstance(created.get(field), str):
            created[field] = datetime.fromisoformat(created[field])

    return created


@api_router.get("/quotations", response_model=List[Quotation])
async def get_quotations(
    quotation_type: Optional[str] = None,
    is_archived: Optional[bool] = None,
    offer_status: Optional[str] = None,
):
    query = {}

    if quotation_type:
        query["quotation_type"] = quotation_type

    if is_archived is None:
        query["is_archived"] = {"$ne": True}
    else:
        query["is_archived"] = bool(is_archived)

    if offer_status and offer_status.lower() != "all":
        query["offer_status"] = offer_status.lower()

    quotations = (
        await db.quotations.find(query, {"_id": 0})
        .sort("date", -1)
        .to_list(1000)
    )

    for q in quotations:
        for field in ["date", "created_at", "updated_at"]:
            if isinstance(q.get(field), str):
                q[field] = datetime.fromisoformat(q[field])

    return quotations


@api_router.get("/quotations/{quotation_id}", response_model=Quotation)
async def get_quotation(quotation_id: str):
    quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    for field in ["date", "created_at", "updated_at"]:
        if isinstance(quotation.get(field), str):
            quotation[field] = datetime.fromisoformat(quotation[field])

    return quotation


@api_router.put("/quotations/{quotation_id}", response_model=Quotation)
async def update_quotation(quotation_id: str, quotation: QuotationUpdate):
    existing = await db.quotations.find_one({"id": quotation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Quotation not found")

    update_dict = {k: v for k, v in quotation.model_dump().items() if v is not None}

    if "customer_id" in update_dict:
        customer = await db.customers.find_one({"id": update_dict["customer_id"]}, {"_id": 0})
        if customer:
            update_dict["customer_name"] = customer.get("name", "")

            contact_person = ""
            contacts = customer.get("contacts", [])
            if contacts:
                primary = next((c for c in contacts if c.get("is_primary")), None)
                contact_person = (primary or contacts[0]).get("name", "")

            update_dict["customer_details"] = {
                "contact_person": contact_person,
                "email": customer.get("email"),
                "phone": customer.get("phone"),
                "address": customer.get("address"),
                "city": customer.get("city"),
                "country": customer.get("country"),
            }

    if "representative_id" in update_dict:
        rep = await db.representatives.find_one({"id": update_dict["representative_id"]}, {"_id": 0})
        if rep:
            update_dict["representative_name"] = rep.get("name", "")
            update_dict["representative_phone"] = rep.get("phone", "")
            update_dict["representative_email"] = rep.get("email", "")

    if "line_items" in update_dict:
        for item in update_dict["line_items"]:
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            calculate_line_totals(item)

        update_dict["totals_by_currency"] = calculate_totals_by_currency(update_dict["line_items"])

    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.quotations.update_one({"id": quotation_id}, {"$set": update_dict})

    updated = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    for field in ["date", "created_at", "updated_at"]:
        if isinstance(updated.get(field), str):
            updated[field] = datetime.fromisoformat(updated[field])
    return updated


@api_router.post("/quotations/{quotation_id}/revise")
async def revise_quotation(quotation_id: str):
    original = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Quotation not found")

    revision_group_id = original.get("revision_group_id", quotation_id)

    all_revisions = await db.quotations.find(
        {"revision_group_id": revision_group_id}, {"_id": 0}
    ).to_list(1000)

    max_revision = max([r.get("revision_no", 0) for r in all_revisions]) if all_revisions else 0
    new_revision_no = max_revision + 1

    base_quote_no = original.get("base_quote_no", original["quote_no"])
    quote_no = f"{base_quote_no}-R{new_revision_no}"

    new_quot = original.copy()
    new_quot["id"] = str(uuid.uuid4())
    new_quot["quote_no"] = quote_no
    new_quot["base_quote_no"] = base_quote_no
    new_quot["revision_no"] = new_revision_no
    new_quot["revision_group_id"] = revision_group_id
    new_quot["date"] = datetime.now(timezone.utc).isoformat()
    new_quot["created_at"] = datetime.now(timezone.utc).isoformat()
    new_quot["updated_at"] = datetime.now(timezone.utc).isoformat()
    new_quot["offer_status"] = "pending"

    await db.quotations.insert_one(new_quot)
    return {"message": "Revision created", "id": new_quot["id"], "quote_no": quote_no}


@api_router.get("/quotations/{quotation_id}/revisions")
async def get_quotation_revisions(quotation_id: str):
    quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    revision_group_id = quotation.get("revision_group_id", quotation_id)

    revisions = (
        await db.quotations.find({"revision_group_id": revision_group_id}, {"_id": 0})
        .sort("revision_no", 1)
        .to_list(1000)
    )

    for rev in revisions:
        for field in ["date", "created_at", "updated_at"]:
            if isinstance(rev.get(field), str):
                rev[field] = datetime.fromisoformat(rev[field])

    return revisions


@api_router.post("/quotations/{quotation_id}/duplicate")
async def duplicate_quotation(quotation_id: str):
    original = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Quotation not found")

    quote_no, base_quote_no = await generate_quote_no(original["quotation_type"], 0)

    new_quot = original.copy()
    new_quot["id"] = str(uuid.uuid4())
    new_quot["quote_no"] = quote_no
    new_quot["base_quote_no"] = base_quote_no
    new_quot["revision_no"] = 0
    new_quot["revision_group_id"] = new_quot["id"]
    new_quot["date"] = datetime.now(timezone.utc).isoformat()
    new_quot["created_at"] = datetime.now(timezone.utc).isoformat()
    new_quot["updated_at"] = datetime.now(timezone.utc).isoformat()
    new_quot["offer_status"] = "pending"

    await db.quotations.insert_one(new_quot)
    return {"message": "Quotation duplicated", "id": new_quot["id"], "quote_no": quote_no}


@api_router.delete("/quotations/{quotation_id}")
async def delete_quotation(quotation_id: str):
    result = await db.quotations.update_one({"id": quotation_id}, {"$set": {"is_archived": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"message": "Quotation archived"}

# ============================================================================
# COST CATEGORY / INTERNAL COST
# ============================================================================
@api_router.post("/cost-categories", response_model=CostCategory)
async def create_cost_category(category: CostCategoryCreate):
    cat_dict = category.model_dump()
    cat_dict["id"] = str(uuid.uuid4())
    cat_dict["is_active"] = True
    cat_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    cat_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.cost_categories.insert_one(cat_dict)
    created = await db.cost_categories.find_one({"id": cat_dict["id"]}, {"_id": 0})

    if isinstance(created["created_at"], str):
        created["created_at"] = datetime.fromisoformat(created["created_at"])
    if isinstance(created["updated_at"], str):
        created["updated_at"] = datetime.fromisoformat(created["updated_at"])
    return created


@api_router.get("/cost-categories", response_model=List[CostCategory])
async def get_cost_categories(is_active: bool = None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    categories = await db.cost_categories.find(query, {"_id": 0}).to_list(1000)
    for cat in categories:
        if isinstance(cat["created_at"], str):
            cat["created_at"] = datetime.fromisoformat(cat["created_at"])
        if isinstance(cat["updated_at"], str):
            cat["updated_at"] = datetime.fromisoformat(cat["updated_at"])
    return categories


@api_router.post("/internal-costs", response_model=InternalCost)
async def create_internal_cost(cost: InternalCostCreate):
    cost_dict = cost.model_dump()
    cost_dict["id"] = str(uuid.uuid4())
    cost_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    cost_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not cost_dict.get("cost_date"):
        cost_dict["cost_date"] = datetime.now(timezone.utc).isoformat()

    category = await db.cost_categories.find_one({"id": cost.category_id}, {"_id": 0})
    if category:
        cost_dict["category_name"] = category["name"]

    await db.internal_costs.insert_one(cost_dict)
    created = await db.internal_costs.find_one({"id": cost_dict["id"]}, {"_id": 0})

    for field in ["cost_date", "created_at", "updated_at"]:
        if isinstance(created[field], str):
            created[field] = datetime.fromisoformat(created[field])
    return created


@api_router.get("/quotations/{quotation_id}/internal-costs", response_model=List[InternalCost])
async def get_quotation_internal_costs(quotation_id: str):
    costs = await db.internal_costs.find({"quotation_id": quotation_id}, {"_id": 0}).to_list(1000)
    for cost in costs:
        for field in ["cost_date", "created_at", "updated_at"]:
            if isinstance(cost[field], str):
                cost[field] = datetime.fromisoformat(cost[field])
    return costs


@api_router.delete("/internal-costs/{cost_id}")
async def delete_internal_cost(cost_id: str):
    result = await db.internal_costs.delete_one({"id": cost_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cost not found")
    return {"message": "Cost deleted"}


# ============================================================================
# COST REPORTS ENDPOINT
# ============================================================================
@api_router.get("/cost-reports")
async def get_cost_reports(
    start_date: str = None,
    end_date: str = None,
    quotation_type: str = None,
    category_id: str = None
):
    """Get aggregated cost reports grouped by category and currency"""
    
    # Build query
    query = {}
    
    if start_date:
        query["cost_date"] = {"$gte": start_date}
    if end_date:
        if "cost_date" in query:
            query["cost_date"]["$lte"] = end_date
        else:
            query["cost_date"] = {"$lte": end_date}
    
    if quotation_type:
        # Get quotation IDs of the specified type
        quotations = await db.quotations.find(
            {"quotation_type": quotation_type}, 
            {"id": 1, "_id": 0}
        ).to_list(10000)
        quotation_ids = [q["id"] for q in quotations]
        query["quotation_id"] = {"$in": quotation_ids}
    
    if category_id:
        query["category_id"] = category_id
    
    # Get all costs matching query
    costs = await db.internal_costs.find(query, {"_id": 0}).to_list(10000)
    
    # Get categories for names
    categories = await db.cost_categories.find({}, {"_id": 0}).to_list(100)
    category_map = {c["id"]: c["name"] for c in categories}
    
    # Aggregate by category and currency
    reports = {}
    for cost in costs:
        cat_id = cost.get("category_id", "unknown")
        cat_name = cost.get("category_name") or category_map.get(cat_id, "Diğer")
        currency = cost.get("currency", "TRY")
        amount = cost.get("amount", 0)
        
        if cat_name not in reports:
            reports[cat_name] = {}
        if currency not in reports[cat_name]:
            reports[cat_name][currency] = 0
        
        reports[cat_name][currency] += amount
    
    return {
        "reports": reports,
        "total_items": len(costs)
    }


# ============================================================================
# FILE UPLOAD ENDPOINTS
# ============================================================================
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@api_router.post("/quotations/{quotation_id}/files")
async def upload_quotation_file(
    quotation_id: str,
    file: UploadFile = File(...),
    category: str = Query(..., description="File category")
):
    quotation = await db.quotations.find_one({"id": quotation_id})
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_metadata = {
        "id": str(uuid.uuid4()),
        "quotation_id": quotation_id,
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "category": category,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }

    await db.quotation_files.insert_one(file_metadata)
    return {"message": "File uploaded", "file_id": file_metadata["id"], "category": category}


@api_router.get("/quotations/{quotation_id}/files")
async def get_quotation_files(quotation_id: str, category: Optional[str] = None):
    query = {"quotation_id": quotation_id}
    if category:
        query["category"] = category

    files = await db.quotation_files.find(query, {"_id": 0}).to_list(1000)
    for f in files:
        if isinstance(f["uploaded_at"], str):
            f["uploaded_at"] = datetime.fromisoformat(f["uploaded_at"])
    return files


@api_router.get("/files/{file_id}")
async def download_file(file_id: str):
    file_metadata = await db.quotation_files.find_one({"id": file_id}, {"_id": 0})
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(file_metadata["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        filename=file_metadata["original_filename"],
        media_type="application/octet-stream"
    )


@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    file_metadata = await db.quotation_files.find_one({"id": file_id}, {"_id": 0})
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(file_metadata["file_path"])
    if file_path.exists():
        file_path.unlink()

    await db.quotation_files.delete_one({"id": file_id})
    return {"message": "File deleted"}

# ============================================================================
# STATS / SEARCH
# ============================================================================
@api_router.get("/statistics")
async def get_statistics():
    base_query = {"is_archived": {"$ne": True}}

    customers = await db.customers.count_documents({"is_active": True})
    products = await db.products.count_documents({"is_active": True})

    total = await db.quotations.count_documents(base_query)
    sales = await db.quotations.count_documents({**base_query, "quotation_type": "sales"})
    service = await db.quotations.count_documents({**base_query, "quotation_type": "service"})

    pending = await db.quotations.count_documents({**base_query, "offer_status": "pending"})
    accepted = await db.quotations.count_documents({**base_query, "offer_status": "accepted"})
    rejected = await db.quotations.count_documents({**base_query, "offer_status": "rejected"})

    return {
        "customers": customers,
        "products": products,
        "total": total,
        "sales": sales,
        "service": service,
        "offer_status": {"pending": pending, "accepted": accepted, "rejected": rejected}
    }


@api_router.get("/search")
async def search_quotations(q: str, quotation_type: str = None):
    query = {
        "$or": [
            {"quote_no": {"$regex": q, "$options": "i"}},
            {"customer_name": {"$regex": q, "$options": "i"}},
            {"subject": {"$regex": q, "$options": "i"}},
            {"project_code": {"$regex": q, "$options": "i"}},
        ]
    }
    if quotation_type:
        query["quotation_type"] = quotation_type

    results = await db.quotations.find(query, {"_id": 0}).limit(50).to_list(50)
    for quot in results:
        for field in ["date", "created_at", "updated_at"]:
            if isinstance(quot[field], str):
                quot[field] = datetime.fromisoformat(quot[field])
    return results

# ============================================================================
# PDF ENDPOINTS
# ============================================================================
@api_router.get("/quotations/{quotation_id}/generate-pdf")
async def generate_quotation_pdf(quotation_id: str):
    browser = None
    try:
        quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")

        frontend_url = os.environ.get("FRONTEND_INTERNAL_URL", "http://localhost:3000")
        preview_url = f"{frontend_url}/quotations/{quotation['quotation_type']}/preview/{quotation_id}"

        browser = await launch(
            headless=True,
            executablePath="/pw-browsers/chromium-1200/chrome-linux/chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        page = await browser.newPage()
        await page.setViewport({"width": 1200, "height": 1600})
        await page.goto(preview_url, {"waitUntil": "networkidle0", "timeout": 45000})
        await asyncio.sleep(3)

        safe_quote_no = quotation["quote_no"].replace("/", "-").replace(" ", "_")
        pdf_path = f"/tmp/teklif_{safe_quote_no}_{quotation_id[:8]}.pdf"

        await page.pdf({
            "path": pdf_path,
            "format": "A4",
            "printBackground": True,
            "margin": {"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
        })

        await browser.close()
        browser = None

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise Exception("PDF file not created or empty")

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"Teklif-{quotation['quote_no']}-{quotation['customer_name']}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")


async def _generate_pdf_v2_impl(quotation_id: str):
    browser = None
    try:
        quotation = await db.quotations.find_one({"id": quotation_id}, {"_id": 0})
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")

        frontend_internal_url = os.environ.get("FRONTEND_INTERNAL_URL", "http://demart-frontend:3000")
        preview_url = f"{frontend_internal_url}/quotations/{quotation['quotation_type']}/preview/{quotation_id}"

        browser = await launch(
            headless=True,
            executablePath="/pw-browsers/chromium-1200/chrome-linux/chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        page = await browser.newPage()
        await page.setViewport({"width": 1200, "height": 1600})
        await page.goto(preview_url, {"waitUntil": "networkidle0", "timeout": 45000})
        await asyncio.sleep(3)

        try:
            await page.emulateMediaType("screen")
        except Exception:
            pass

        safe_quote_no = quotation["quote_no"].replace("/", "-").replace(" ", "_")
        pdf_path = f"/tmp/teklif_{safe_quote_no}_{quotation_id[:8]}_v2.pdf"

        await page.pdf({
            "path": pdf_path,
            "format": "A4",
            "printBackground": True,
            "margin": {"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
        })

        await browser.close()
        browser = None

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise Exception("PDF file not created or empty")

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"Teklif-{quotation['quote_no']}-{quotation['customer_name']}.pdf",
        )

    except HTTPException:
        raise
    except Exception as e:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"PDF generation failed (v2): {e}")


@api_router.get("/quotations/{quotation_id}/generate-pdf-v2")
async def generate_quotation_pdf_v2_endpoint(quotation_id: str):
    return await _generate_pdf_v2_impl(quotation_id)


# ============================================================================
# EDITED PDF UPLOAD/DOWNLOAD
# ============================================================================

EDITED_PDF_DIR = Path("uploads/edited_pdfs")
EDITED_PDF_DIR.mkdir(parents=True, exist_ok=True)

@api_router.post("/quotations/{quotation_id}/upload-edited-pdf")
async def upload_edited_pdf(quotation_id: str, file: UploadFile = File(...)):
    """Upload an edited/corrected PDF for a quotation"""
    # Verify quotation exists
    quotation = await db.quotations.find_one({"id": quotation_id})
    if not quotation:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyası yüklenebilir")
    
    # Save the file
    file_path = EDITED_PDF_DIR / f"{quotation_id}_edited.pdf"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update quotation record
    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {
            "has_edited_pdf": True,
            "edited_pdf_path": str(file_path),
            "edited_pdf_uploaded_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"ok": True, "message": "Düzenlenmiş PDF başarıyla yüklendi"}


@api_router.get("/quotations/{quotation_id}/download-edited-pdf")
async def download_edited_pdf(quotation_id: str):
    """Download the edited PDF for a quotation"""
    quotation = await db.quotations.find_one({"id": quotation_id})
    if not quotation:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")
    
    if not quotation.get("has_edited_pdf"):
        raise HTTPException(status_code=404, detail="Bu teklif için düzenlenmiş PDF bulunamadı")
    
    file_path = Path(quotation.get("edited_pdf_path", ""))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF dosyası bulunamadı")
    
    # Get quotation info for filename
    quote_no = quotation.get("quote_no", quotation_id)
    customer_name = quotation.get("customer_name", "").replace(" ", "_")[:30]
    
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"Teklif-{quote_no}-{customer_name}-DUZENLENMIS.pdf"
    )


@api_router.delete("/quotations/{quotation_id}/delete-edited-pdf")
async def delete_edited_pdf(quotation_id: str):
    """Delete the edited PDF for a quotation"""
    quotation = await db.quotations.find_one({"id": quotation_id})
    if not quotation:
        raise HTTPException(status_code=404, detail="Teklif bulunamadı")
    
    file_path = Path(quotation.get("edited_pdf_path", ""))
    if file_path.exists():
        file_path.unlink()
    
    await db.quotations.update_one(
        {"id": quotation_id},
        {"$set": {
            "has_edited_pdf": False,
            "edited_pdf_path": None,
            "edited_pdf_uploaded_at": None
        }}
    )
    
    return {"ok": True, "message": "Düzenlenmiş PDF silindi"}


# ============================================================================
# APP MOUNT
# ============================================================================
app.include_router(api_router, prefix="/api")

# Static files for uploads directory
uploads_path = Path(__file__).parent.parent / "uploads"
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

@app.get("/")
async def root():
    return {"message": "Quotation Management API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
