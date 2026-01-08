from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4
from inventory_models import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItem,
    INVENTORY_CATEGORIES
)

router = APIRouter(tags=["Inventory"])

_db = None

def set_database(db):
    global _db
    _db = db

async def generate_inventory_no(category: str) -> str:
    """Generate next inventory number for category"""
    prefix = INVENTORY_CATEGORIES.get(category, {}).get("prefix", "D-X")
    
    # Find the highest number for this category
    last_item = await _db.inventory_items.find_one(
        {"category": category, "is_deleted": {"$ne": True}},
        sort=[("inventory_no", -1)]
    )
    
    if last_item:
        # Extract the number from the inventory_no (e.g., "D-O-05" -> 5)
        try:
            last_no = int(last_item["inventory_no"].split("-")[-1])
            next_no = last_no + 1
        except:
            next_no = 1
    else:
        next_no = 1
    
    return f"{prefix}-{next_no:02d}"

@router.get("/categories")
async def get_categories():
    """Get all inventory categories with stats"""
    result = []
    for key, value in INVENTORY_CATEGORIES.items():
        # Count active items
        active_count = await _db.inventory_items.count_documents({
            "category": key,
            "is_deleted": {"$ne": True},
            "is_retired": {"$ne": True}
        })
        # Count retired items
        retired_count = await _db.inventory_items.count_documents({
            "category": key,
            "is_deleted": {"$ne": True},
            "is_retired": True
        })
        # Sum total cost
        pipeline = [
            {"$match": {"category": key, "is_deleted": {"$ne": True}, "is_retired": {"$ne": True}}},
            {"$group": {"_id": None, "total": {"$sum": {"$multiply": ["$purchase_price", "$quantity"]}}}}
        ]
        total_agg = await _db.inventory_items.aggregate(pipeline).to_list(1)
        total_cost = total_agg[0]["total"] if total_agg else 0
        
        result.append({
            "key": key,
            "name": value["name"],
            "prefix": value["prefix"],
            "active_count": active_count,
            "retired_count": retired_count,
            "total_cost": total_cost
        })
    return result

@router.get("/items")
async def get_inventory_items(category: Optional[str] = None, include_retired: bool = False):
    """Get inventory items, optionally filtered by category"""
    query = {"is_deleted": {"$ne": True}}
    if category:
        query["category"] = category
    if not include_retired:
        query["is_retired"] = {"$ne": True}
    
    items = await _db.inventory_items.find(query, {"_id": 0}).sort("inventory_no", 1).to_list(1000)
    return items

@router.get("/items/retired")
async def get_retired_items(category: Optional[str] = None):
    """Get only retired inventory items"""
    query = {"is_deleted": {"$ne": True}, "is_retired": True}
    if category:
        query["category"] = category
    
    items = await _db.inventory_items.find(query, {"_id": 0}).sort("inventory_no", 1).to_list(1000)
    return items

@router.post("/items")
async def create_inventory_item(body: InventoryItemCreate):
    """Create a new inventory item"""
    if body.category not in INVENTORY_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Geçersiz kategori. Geçerli kategoriler: {list(INVENTORY_CATEGORIES.keys())}")
    
    inventory_no = await generate_inventory_no(body.category)
    now = datetime.now(timezone.utc)
    
    item = {
        "id": str(uuid4()),
        "inventory_no": inventory_no,
        "category": body.category,
        "description": body.description,
        "purchase_date": body.purchase_date,
        "quantity": body.quantity,
        "purchase_price": body.purchase_price,
        "notes": body.notes,
        "is_retired": False,
        "retirement_reason": None,
        "is_deleted": False,
        "created_at": now,
        "updated_at": now
    }
    
    await _db.inventory_items.insert_one(item)
    del item["_id"]
    return item

@router.put("/items/{item_id}")
async def update_inventory_item(item_id: str, body: InventoryItemUpdate):
    """Update an inventory item"""
    update_data = body.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await _db.inventory_items.update_one(
        {"id": item_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Envanter bulunamadı")
    
    item = await _db.inventory_items.find_one({"id": item_id}, {"_id": 0})
    return item

@router.delete("/items/{item_id}")
async def delete_inventory_item(item_id: str):
    """Soft delete an inventory item"""
    result = await _db.inventory_items.update_one(
        {"id": item_id},
        {"$set": {"is_deleted": True, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Envanter bulunamadı")
    
    return {"ok": True, "message": "Envanter silindi"}

@router.post("/items/{item_id}/retire")
async def retire_inventory_item(item_id: str, reason: str = ""):
    """Mark an inventory item as retired"""
    result = await _db.inventory_items.update_one(
        {"id": item_id},
        {"$set": {
            "is_retired": True,
            "retirement_reason": reason,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Envanter bulunamadı")
    
    return {"ok": True, "message": "Envanter envanterden çıkarıldı"}

@router.post("/items/{item_id}/restore")
async def restore_inventory_item(item_id: str):
    """Restore a retired inventory item"""
    result = await _db.inventory_items.update_one(
        {"id": item_id},
        {"$set": {
            "is_retired": False,
            "retirement_reason": None,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Envanter bulunamadı")
    
    return {"ok": True, "message": "Envanter geri alındı"}

@router.get("/summary")
async def get_inventory_summary():
    """Get overall inventory summary"""
    total_items = await _db.inventory_items.count_documents({"is_deleted": {"$ne": True}, "is_retired": {"$ne": True}})
    retired_items = await _db.inventory_items.count_documents({"is_deleted": {"$ne": True}, "is_retired": True})
    
    # Total investment
    pipeline = [
        {"$match": {"is_deleted": {"$ne": True}, "is_retired": {"$ne": True}}},
        {"$group": {"_id": None, "total": {"$sum": {"$multiply": ["$purchase_price", "$quantity"]}}}}
    ]
    total_agg = await _db.inventory_items.aggregate(pipeline).to_list(1)
    total_investment = total_agg[0]["total"] if total_agg else 0
    
    # Retired value
    pipeline_retired = [
        {"$match": {"is_deleted": {"$ne": True}, "is_retired": True}},
        {"$group": {"_id": None, "total": {"$sum": {"$multiply": ["$purchase_price", "$quantity"]}}}}
    ]
    retired_agg = await _db.inventory_items.aggregate(pipeline_retired).to_list(1)
    retired_value = retired_agg[0]["total"] if retired_agg else 0
    
    return {
        "total_items": total_items,
        "retired_items": retired_items,
        "total_investment": total_investment,
        "retired_value": retired_value
    }
