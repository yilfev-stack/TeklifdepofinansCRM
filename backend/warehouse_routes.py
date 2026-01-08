"""
Advanced Warehouse Management System API
Supports: Multiple Warehouses, Rack Groups, Levels, Compartments, Variant-based Stock
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from warehouse_models import (
    WarehouseCreate, WarehouseUpdate, Warehouse,
    RackGroupCreate, RackGroupUpdate, RackGroup,
    RackLevelCreate, RackLevelUpdate, RackLevel,
    RackSlotCreate, RackSlotUpdate, RackSlot,
    StockItemCreate, StockItem,
    StockMovementCreate, StockMovement, StockMovementType,
    InventoryCountCreate, InventoryCount,
    StockReservation
)

router = APIRouter()
_db = None


def init_warehouse_db(db):
    global _db
    _db = db


def _now():
    return datetime.now(timezone.utc)


def _require_db():
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")


# ==================== HELPER FUNCTIONS ====================

async def build_full_address(warehouse_id: str, rack_group_id: str, rack_level_id: str, rack_slot_id: str) -> str:
    """Build full address string like: Maltepe Depo / A Rafı / 5. Kat / Bölme 1"""
    parts = []
    
    warehouse = await _db.warehouses.find_one({"id": warehouse_id}, {"_id": 0})
    if warehouse:
        parts.append(warehouse.get("name", ""))
    
    rack_group = await _db.rack_groups.find_one({"id": rack_group_id}, {"_id": 0})
    if rack_group:
        parts.append(rack_group.get("name", ""))
    
    rack_level = await _db.rack_levels.find_one({"id": rack_level_id}, {"_id": 0})
    if rack_level:
        level_name = rack_level.get("name") or f"{rack_level.get('level_number', '')}. Kat"
        parts.append(level_name)
    
    rack_slot = await _db.rack_slots.find_one({"id": rack_slot_id}, {"_id": 0})
    if rack_slot:
        slot_name = rack_slot.get("name") or f"Bölme {rack_slot.get('slot_number', '')}"
        parts.append(slot_name)
    
    return " / ".join(parts)


# ==================== WAREHOUSES ====================

@router.get("/warehouses")
async def list_warehouses(include_deleted: bool = False):
    _require_db()
    query = {} if include_deleted else {"is_deleted": {"$ne": True}}
    cursor = _db.warehouses.find(query, {"_id": 0}).sort("name", 1)
    return await cursor.to_list(length=100)


@router.get("/warehouses/{warehouse_id}")
async def get_warehouse(warehouse_id: str):
    _require_db()
    doc = await _db.warehouses.find_one({"id": warehouse_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return doc


@router.post("/warehouses")
async def create_warehouse(body: WarehouseCreate):
    _require_db()
    existing = await _db.warehouses.find_one({"code": body.code, "is_deleted": {"$ne": True}})
    if existing:
        raise HTTPException(status_code=400, detail="Warehouse code already exists")
    
    doc = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "code": body.code,
        "address": body.address,
        "description": body.description,
        "is_active": True,
        "is_deleted": False,
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
    }
    await _db.warehouses.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.put("/warehouses/{warehouse_id}")
async def update_warehouse(warehouse_id: str, body: WarehouseUpdate):
    _require_db()
    existing = await _db.warehouses.find_one({"id": warehouse_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updates["updated_at"] = _now().isoformat()
    
    await _db.warehouses.update_one({"id": warehouse_id}, {"$set": updates})
    return await _db.warehouses.find_one({"id": warehouse_id}, {"_id": 0})


@router.delete("/warehouses/{warehouse_id}")
async def delete_warehouse(warehouse_id: str, hard: bool = False):
    _require_db()
    if hard:
        result = await _db.warehouses.delete_one({"id": warehouse_id})
    else:
        result = await _db.warehouses.update_one(
            {"id": warehouse_id}, 
            {"$set": {"is_deleted": True, "updated_at": _now().isoformat()}}
        )
    
    if result.modified_count == 0 and result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"ok": True}


# ==================== RACK GROUPS ====================

@router.get("/rack-groups")
async def list_rack_groups(warehouse_id: Optional[str] = None):
    _require_db()
    query = {"is_deleted": {"$ne": True}}
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    cursor = _db.rack_groups.find(query, {"_id": 0}).sort("code", 1)
    return await cursor.to_list(length=500)


@router.get("/rack-groups/{rack_group_id}")
async def get_rack_group(rack_group_id: str):
    _require_db()
    doc = await _db.rack_groups.find_one({"id": rack_group_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Rack group not found")
    return doc


@router.post("/rack-groups")
async def create_rack_group(body: RackGroupCreate):
    _require_db()
    # Verify warehouse exists
    warehouse = await _db.warehouses.find_one({"id": body.warehouse_id})
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    existing = await _db.rack_groups.find_one({
        "warehouse_id": body.warehouse_id, 
        "code": body.code, 
        "is_deleted": {"$ne": True}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Rack group code already exists in this warehouse")
    
    doc = {
        "id": str(uuid.uuid4()),
        "warehouse_id": body.warehouse_id,
        "name": body.name,
        "code": body.code,
        "description": body.description,
        "is_active": True,
        "is_deleted": False,
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
    }
    await _db.rack_groups.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.put("/rack-groups/{rack_group_id}")
async def update_rack_group(rack_group_id: str, body: RackGroupUpdate):
    _require_db()
    existing = await _db.rack_groups.find_one({"id": rack_group_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Rack group not found")
    
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updates["updated_at"] = _now().isoformat()
    
    await _db.rack_groups.update_one({"id": rack_group_id}, {"$set": updates})
    return await _db.rack_groups.find_one({"id": rack_group_id}, {"_id": 0})


@router.delete("/rack-groups/{rack_group_id}")
async def delete_rack_group(rack_group_id: str):
    _require_db()
    result = await _db.rack_groups.update_one(
        {"id": rack_group_id}, 
        {"$set": {"is_deleted": True, "updated_at": _now().isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Rack group not found")
    return {"ok": True}


# ==================== RACK LEVELS ====================

@router.get("/rack-levels")
async def list_rack_levels(rack_group_id: Optional[str] = None):
    _require_db()
    query = {"is_deleted": {"$ne": True}}
    if rack_group_id:
        query["rack_group_id"] = rack_group_id
    cursor = _db.rack_levels.find(query, {"_id": 0}).sort("level_number", 1)
    return await cursor.to_list(length=500)


@router.post("/rack-levels")
async def create_rack_level(body: RackLevelCreate):
    _require_db()
    rack_group = await _db.rack_groups.find_one({"id": body.rack_group_id})
    if not rack_group:
        raise HTTPException(status_code=404, detail="Rack group not found")
    
    doc = {
        "id": str(uuid.uuid4()),
        "rack_group_id": body.rack_group_id,
        "level_number": body.level_number,
        "name": body.name or f"{body.level_number}. Kat",
        "is_active": True,
        "is_deleted": False,
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
    }
    await _db.rack_levels.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.delete("/rack-levels/{rack_level_id}")
async def delete_rack_level(rack_level_id: str):
    _require_db()
    result = await _db.rack_levels.update_one(
        {"id": rack_level_id}, 
        {"$set": {"is_deleted": True, "updated_at": _now().isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Rack level not found")
    return {"ok": True}


# ==================== RACK SLOTS (COMPARTMENTS) ====================

@router.get("/rack-slots")
async def list_rack_slots(rack_level_id: Optional[str] = None):
    _require_db()
    query = {"is_deleted": {"$ne": True}}
    if rack_level_id:
        query["rack_level_id"] = rack_level_id
    cursor = _db.rack_slots.find(query, {"_id": 0}).sort("slot_number", 1)
    return await cursor.to_list(length=1000)


@router.post("/rack-slots")
async def create_rack_slot(body: RackSlotCreate):
    _require_db()
    rack_level = await _db.rack_levels.find_one({"id": body.rack_level_id})
    if not rack_level:
        raise HTTPException(status_code=404, detail="Rack level not found")
    
    doc = {
        "id": str(uuid.uuid4()),
        "rack_level_id": body.rack_level_id,
        "slot_number": body.slot_number,
        "name": body.name or f"Bölme {body.slot_number}",
        "is_active": True,
        "is_deleted": False,
        "created_at": _now().isoformat(),
        "updated_at": _now().isoformat(),
    }
    await _db.rack_slots.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.delete("/rack-slots/{rack_slot_id}")
async def delete_rack_slot(rack_slot_id: str):
    _require_db()
    result = await _db.rack_slots.update_one(
        {"id": rack_slot_id}, 
        {"$set": {"is_deleted": True, "updated_at": _now().isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Rack slot not found")
    return {"ok": True}


# ==================== STOCK ITEMS ====================

@router.get("/stock")
async def list_stock(
    warehouse_id: Optional[str] = None,
    rack_group_id: Optional[str] = None,
    product_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    low_stock_only: bool = False
):
    _require_db()
    query = {}
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    if rack_group_id:
        query["rack_group_id"] = rack_group_id
    if product_id:
        query["product_id"] = product_id
    if variant_id:
        query["variant_id"] = variant_id
    
    cursor = _db.stock_items.find(query, {"_id": 0}).sort("full_address", 1)
    items = await cursor.to_list(length=5000)
    
    if low_stock_only:
        items = [i for i in items if i.get("quantity", 0) <= i.get("min_stock", 0)]
    
    return items


@router.get("/stock/summary")
async def get_stock_summary(warehouse_id: Optional[str] = None):
    """Get stock summary grouped by variant"""
    _require_db()
    pipeline = [
        {"$match": {"warehouse_id": warehouse_id} if warehouse_id else {}},
        {"$group": {
            "_id": {"product_id": "$product_id", "variant_id": "$variant_id"},
            "variant_name": {"$first": "$variant_name"},
            "variant_sku": {"$first": "$variant_sku"},
            "total_quantity": {"$sum": "$quantity"},
            "total_reserved": {"$sum": "$reserved_quantity"},
            "locations_count": {"$sum": 1},
            "min_stock": {"$max": "$min_stock"}
        }},
        {"$project": {
            "_id": 0,
            "product_id": "$_id.product_id",
            "variant_id": "$_id.variant_id",
            "variant_name": 1,
            "variant_sku": 1,
            "total_quantity": 1,
            "total_reserved": 1,
            "available_quantity": {"$subtract": ["$total_quantity", "$total_reserved"]},
            "locations_count": 1,
            "min_stock": 1,
            "is_low_stock": {"$lte": ["$total_quantity", "$min_stock"]}
        }}
    ]
    cursor = _db.stock_items.aggregate(pipeline)
    return await cursor.to_list(length=5000)


@router.get("/stock/low-stock")
async def get_low_stock():
    """Get items below minimum stock level"""
    _require_db()
    pipeline = [
        {"$group": {
            "_id": {"product_id": "$product_id", "variant_id": "$variant_id"},
            "variant_name": {"$first": "$variant_name"},
            "total_quantity": {"$sum": "$quantity"},
            "min_stock": {"$max": "$min_stock"}
        }},
        {"$match": {"$expr": {"$lte": ["$total_quantity", "$min_stock"]}}},
        {"$project": {
            "_id": 0,
            "product_id": "$_id.product_id",
            "variant_id": "$_id.variant_id",
            "variant_name": 1,
            "total_quantity": 1,
            "min_stock": 1,
            "shortage": {"$subtract": ["$min_stock", "$total_quantity"]}
        }}
    ]
    cursor = _db.stock_items.aggregate(pipeline)
    return await cursor.to_list(length=500)


# ==================== STOCK MOVEMENTS ====================

@router.post("/stock/in")
async def stock_in(body: StockMovementCreate):
    """Add stock to a location"""
    _require_db()
    
    full_address = await build_full_address(
        body.warehouse_id, body.rack_group_id, body.rack_level_id, body.rack_slot_id
    )
    
    # Find or create stock item - use product_id if no variant
    stock_query = {
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "product_id": body.product_id,
    }
    if body.variant_id:
        stock_query["variant_id"] = body.variant_id
    else:
        stock_query["$or"] = [{"variant_id": None}, {"variant_id": ""}]
    
    stock_item = await _db.stock_items.find_one(stock_query)
    
    if stock_item:
        new_qty = stock_item.get("quantity", 0) + body.quantity
        await _db.stock_items.update_one(
            {"id": stock_item["id"]},
            {"$set": {"quantity": new_qty, "updated_at": _now().isoformat()}}
        )
    else:
        stock_doc = {
            "id": str(uuid.uuid4()),
            "warehouse_id": body.warehouse_id,
            "rack_group_id": body.rack_group_id,
            "rack_level_id": body.rack_level_id,
            "rack_slot_id": body.rack_slot_id,
            "product_id": body.product_id,
            "variant_id": body.variant_id,
            "variant_name": body.variant_name,
            "quantity": body.quantity,
            "reserved_quantity": 0,
            "min_stock": 0,
            "full_address": full_address,
            "created_at": _now().isoformat(),
            "updated_at": _now().isoformat(),
        }
        await _db.stock_items.insert_one(stock_doc)
    
    # Log movement
    movement_doc = {
        "id": str(uuid.uuid4()),
        "movement_type": StockMovementType.IN,
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "product_id": body.product_id,
        "variant_id": body.variant_id,
        "variant_name": body.variant_name,
        "quantity": body.quantity,
        "source_address": full_address,
        "reference": body.reference,
        "note": body.note,
        "created_at": _now().isoformat(),
    }
    await _db.stock_movements.insert_one(movement_doc)
    
    return {"ok": True, "address": full_address, "quantity": body.quantity}


@router.post("/stock/out")
async def stock_out(body: StockMovementCreate):
    """Remove stock from a location"""
    _require_db()
    
    stock_item = await _db.stock_items.find_one({
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "variant_id": body.variant_id
    })
    
    if not stock_item:
        raise HTTPException(status_code=404, detail="Stock not found at this location")
    
    current_qty = stock_item.get("quantity", 0)
    reserved_qty = stock_item.get("reserved_quantity", 0)
    available_qty = current_qty - reserved_qty
    
    # Check if enough stock available
    if body.quantity > available_qty:
        raise HTTPException(
            status_code=400, 
            detail=f"Yetersiz stok. Mevcut: {current_qty}, Rezerve: {reserved_qty}, Kullanılabilir: {available_qty}, İstenen: {body.quantity}"
        )
    
    new_qty = current_qty - body.quantity
    
    await _db.stock_items.update_one(
        {"id": stock_item["id"]},
        {"$set": {"quantity": new_qty, "updated_at": _now().isoformat()}}
    )
    
    full_address = await build_full_address(
        body.warehouse_id, body.rack_group_id, body.rack_level_id, body.rack_slot_id
    )
    
    movement_doc = {
        "id": str(uuid.uuid4()),
        "movement_type": StockMovementType.OUT,
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "product_id": body.product_id,
        "variant_id": body.variant_id,
        "variant_name": body.variant_name,
        "quantity": -body.quantity,
        "source_address": full_address,
        "reference": body.reference,
        "note": body.note,
        "created_at": _now().isoformat(),
    }
    await _db.stock_movements.insert_one(movement_doc)
    
    return {"ok": True, "address": full_address, "new_quantity": new_qty}


@router.post("/stock/transfer")
async def stock_transfer(body: StockMovementCreate):
    """Transfer stock between locations"""
    _require_db()
    
    if not body.target_warehouse_id or not body.target_rack_slot_id:
        raise HTTPException(status_code=400, detail="Target location required for transfer")
    
    # Check source stock
    source_item = await _db.stock_items.find_one({
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "variant_id": body.variant_id
    })
    
    if not source_item:
        raise HTTPException(status_code=404, detail="Source stock not found")
    
    if source_item.get("quantity", 0) < body.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for transfer")
    
    # Decrease source
    await _db.stock_items.update_one(
        {"id": source_item["id"]},
        {"$inc": {"quantity": -body.quantity}, "$set": {"updated_at": _now().isoformat()}}
    )
    
    # Increase target
    target_address = await build_full_address(
        body.target_warehouse_id, body.target_rack_group_id, 
        body.target_rack_level_id, body.target_rack_slot_id
    )
    
    target_item = await _db.stock_items.find_one({
        "warehouse_id": body.target_warehouse_id,
        "rack_group_id": body.target_rack_group_id,
        "rack_level_id": body.target_rack_level_id,
        "rack_slot_id": body.target_rack_slot_id,
        "variant_id": body.variant_id
    })
    
    if target_item:
        await _db.stock_items.update_one(
            {"id": target_item["id"]},
            {"$inc": {"quantity": body.quantity}, "$set": {"updated_at": _now().isoformat()}}
        )
    else:
        stock_doc = {
            "id": str(uuid.uuid4()),
            "warehouse_id": body.target_warehouse_id,
            "rack_group_id": body.target_rack_group_id,
            "rack_level_id": body.target_rack_level_id,
            "rack_slot_id": body.target_rack_slot_id,
            "product_id": body.product_id,
            "variant_id": body.variant_id,
            "variant_name": body.variant_name,
            "quantity": body.quantity,
            "reserved_quantity": 0,
            "min_stock": 0,
            "full_address": target_address,
            "created_at": _now().isoformat(),
            "updated_at": _now().isoformat(),
        }
        await _db.stock_items.insert_one(stock_doc)
    
    source_address = await build_full_address(
        body.warehouse_id, body.rack_group_id, body.rack_level_id, body.rack_slot_id
    )
    
    movement_doc = {
        "id": str(uuid.uuid4()),
        "movement_type": StockMovementType.TRANSFER,
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "target_warehouse_id": body.target_warehouse_id,
        "target_rack_group_id": body.target_rack_group_id,
        "target_rack_level_id": body.target_rack_level_id,
        "target_rack_slot_id": body.target_rack_slot_id,
        "product_id": body.product_id,
        "variant_id": body.variant_id,
        "variant_name": body.variant_name,
        "quantity": body.quantity,
        "source_address": source_address,
        "target_address": target_address,
        "reference": body.reference,
        "note": body.note,
        "created_at": _now().isoformat(),
    }
    await _db.stock_movements.insert_one(movement_doc)
    
    return {"ok": True, "from": source_address, "to": target_address, "quantity": body.quantity}


@router.get("/movements")
async def list_movements(
    warehouse_id: Optional[str] = None,
    movement_type: Optional[str] = None,
    limit: int = 100
):
    _require_db()
    query = {}
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    if movement_type:
        query["movement_type"] = movement_type
    
    cursor = _db.stock_movements.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


# ==================== STOCK ITEM CRUD ====================

@router.put("/stock/{stock_id}")
async def update_stock_item(stock_id: str, quantity: float, note: str = ""):
    """Update stock item quantity"""
    _require_db()
    
    stock_item = await _db.stock_items.find_one({"id": stock_id})
    if not stock_item:
        raise HTTPException(status_code=404, detail="Stok kaydı bulunamadı")
    
    old_quantity = stock_item.get("quantity", 0)
    difference = quantity - old_quantity
    
    await _db.stock_items.update_one(
        {"id": stock_id},
        {"$set": {"quantity": quantity, "updated_at": _now().isoformat()}}
    )
    
    # Log the adjustment
    movement_doc = {
        "id": str(uuid.uuid4()),
        "movement_type": "ADJUSTMENT",
        "warehouse_id": stock_item.get("warehouse_id"),
        "rack_group_id": stock_item.get("rack_group_id"),
        "rack_level_id": stock_item.get("rack_level_id"),
        "rack_slot_id": stock_item.get("rack_slot_id"),
        "product_id": stock_item.get("product_id"),
        "variant_id": stock_item.get("variant_id"),
        "variant_name": stock_item.get("variant_name"),
        "quantity": difference,
        "source_address": stock_item.get("full_address"),
        "target_address": None,
        "reference": f"Manuel düzeltme: {old_quantity} → {quantity}",
        "note": note or "Stok miktarı manuel düzeltildi",
        "created_at": _now().isoformat(),
    }
    await _db.stock_movements.insert_one(movement_doc)
    
    return {"ok": True, "old_quantity": old_quantity, "new_quantity": quantity}


@router.delete("/stock/{stock_id}")
async def delete_stock_item(stock_id: str):
    """Delete stock item"""
    _require_db()
    
    stock_item = await _db.stock_items.find_one({"id": stock_id})
    if not stock_item:
        raise HTTPException(status_code=404, detail="Stok kaydı bulunamadı")
    
    # Log the deletion
    movement_doc = {
        "id": str(uuid.uuid4()),
        "movement_type": "DELETE",
        "warehouse_id": stock_item.get("warehouse_id"),
        "rack_group_id": stock_item.get("rack_group_id"),
        "rack_level_id": stock_item.get("rack_level_id"),
        "rack_slot_id": stock_item.get("rack_slot_id"),
        "product_id": stock_item.get("product_id"),
        "variant_id": stock_item.get("variant_id"),
        "variant_name": stock_item.get("variant_name"),
        "quantity": -stock_item.get("quantity", 0),
        "source_address": stock_item.get("full_address"),
        "target_address": None,
        "reference": "Stok kaydı silindi",
        "note": f"Silinen miktar: {stock_item.get('quantity', 0)}",
        "created_at": _now().isoformat(),
    }
    await _db.stock_movements.insert_one(movement_doc)
    
    await _db.stock_items.delete_one({"id": stock_id})
    
    return {"ok": True, "message": "Stok kaydı silindi"}


# ==================== INVENTORY COUNT ====================

@router.post("/inventory-count")
async def create_inventory_count(body: InventoryCountCreate):
    """Record an inventory count"""
    _require_db()
    
    full_address = await build_full_address(
        body.warehouse_id, body.rack_group_id or "", 
        body.rack_level_id or "", body.rack_slot_id or ""
    )
    
    doc = {
        "id": str(uuid.uuid4()),
        "warehouse_id": body.warehouse_id,
        "rack_group_id": body.rack_group_id,
        "rack_level_id": body.rack_level_id,
        "rack_slot_id": body.rack_slot_id,
        "product_id": body.product_id,
        "variant_id": body.variant_id,
        "full_address": full_address,
        "system_quantity": body.system_quantity,
        "counted_quantity": body.counted_quantity,
        "difference": body.counted_quantity - body.system_quantity,
        "is_approved": False,
        "note": body.note,
        "created_at": _now().isoformat(),
    }
    await _db.inventory_counts.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.post("/inventory-count/{count_id}/approve")
async def approve_inventory_count(count_id: str):
    """Approve and apply inventory count adjustment"""
    _require_db()
    
    count = await _db.inventory_counts.find_one({"id": count_id})
    if not count:
        raise HTTPException(status_code=404, detail="Inventory count not found")
    
    if count.get("is_approved"):
        raise HTTPException(status_code=400, detail="Already approved")
    
    # Update stock with counted quantity
    stock_item = await _db.stock_items.find_one({
        "warehouse_id": count["warehouse_id"],
        "rack_group_id": count.get("rack_group_id"),
        "rack_level_id": count.get("rack_level_id"),
        "rack_slot_id": count.get("rack_slot_id"),
        "variant_id": count["variant_id"]
    })
    
    if stock_item:
        await _db.stock_items.update_one(
            {"id": stock_item["id"]},
            {"$set": {"quantity": count["counted_quantity"], "updated_at": _now().isoformat()}}
        )
    
    # Mark as approved
    await _db.inventory_counts.update_one(
        {"id": count_id},
        {"$set": {"is_approved": True, "approved_at": _now().isoformat()}}
    )
    
    # Log movement
    movement_doc = {
        "id": str(uuid.uuid4()),
        "movement_type": StockMovementType.ADJUST,
        "warehouse_id": count["warehouse_id"],
        "rack_group_id": count.get("rack_group_id"),
        "rack_level_id": count.get("rack_level_id"),
        "rack_slot_id": count.get("rack_slot_id"),
        "product_id": count["product_id"],
        "variant_id": count["variant_id"],
        "quantity": count["difference"],
        "source_address": count.get("full_address"),
        "note": f"Sayım düzeltmesi: {count['system_quantity']} → {count['counted_quantity']}",
        "created_at": _now().isoformat(),
    }
    await _db.stock_movements.insert_one(movement_doc)
    
    return {"ok": True, "adjustment": count["difference"]}


@router.get("/inventory-counts")
async def list_inventory_counts(pending_only: bool = False):
    _require_db()
    query = {"is_approved": False} if pending_only else {}
    cursor = _db.inventory_counts.find(query, {"_id": 0}).sort("created_at", -1)
    return await cursor.to_list(length=500)


# ==================== REPORTS ====================

@router.get("/reports/by-warehouse")
async def report_by_warehouse():
    """Stock report grouped by warehouse"""
    _require_db()
    pipeline = [
        {"$group": {
            "_id": "$warehouse_id",
            "total_items": {"$sum": 1},
            "total_quantity": {"$sum": "$quantity"},
            "total_reserved": {"$sum": "$reserved_quantity"},
        }},
        {"$project": {
            "_id": 0,
            "warehouse_id": "$_id",
            "total_items": 1,
            "total_quantity": 1,
            "total_reserved": 1
        }}
    ]
    cursor = _db.stock_items.aggregate(pipeline)
    items = await cursor.to_list(length=100)
    
    # Add warehouse names
    for item in items:
        wh = await _db.warehouses.find_one({"id": item["warehouse_id"]}, {"_id": 0})
        item["warehouse_name"] = wh.get("name", "") if wh else ""
    
    return items


@router.get("/reports/by-product")
async def report_by_product():
    """Stock report grouped by product variant"""
    _require_db()
    pipeline = [
        {"$group": {
            "_id": {"product_id": "$product_id", "variant_id": "$variant_id"},
            "variant_name": {"$first": "$variant_name"},
            "total_quantity": {"$sum": "$quantity"},
            "total_reserved": {"$sum": "$reserved_quantity"},
            "locations_count": {"$sum": 1},
            "min_stock": {"$max": "$min_stock"},
            "locations": {"$push": "$full_address"}
        }},
        {"$project": {
            "_id": 0,
            "product_id": "$_id.product_id",
            "variant_id": "$_id.variant_id",
            "variant_name": 1,
            "total_quantity": 1,
            "total_reserved": 1,
            "available": {"$subtract": ["$total_quantity", "$total_reserved"]},
            "locations_count": 1,
            "min_stock": 1,
            "is_low_stock": {"$lte": ["$total_quantity", "$min_stock"]},
            "locations": 1
        }}
    ]
    cursor = _db.stock_items.aggregate(pipeline)
    return await cursor.to_list(length=500)


# Legacy endpoints for backwards compatibility
@router.get("/locations")
async def list_locations_legacy():
    """Legacy endpoint - returns warehouses"""
    return await list_warehouses()
