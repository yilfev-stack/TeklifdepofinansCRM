"""
Advanced Warehouse Management System Models
Supports: Multiple Warehouses, Rack Groups, Levels, Compartments, Variant-based Stock
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid


def _now():
    return datetime.now(timezone.utc)


# ==================== WAREHOUSE ====================
class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    description: Optional[str] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Warehouse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    code: str
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ==================== RACK GROUP ====================
class RackGroupCreate(BaseModel):
    warehouse_id: str
    name: str
    code: str
    description: Optional[str] = None


class RackGroupUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RackGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    warehouse_id: str
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ==================== RACK LEVEL ====================
class RackLevelCreate(BaseModel):
    rack_group_id: str
    level_number: int
    name: Optional[str] = None


class RackLevelUpdate(BaseModel):
    level_number: Optional[int] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class RackLevel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rack_group_id: str
    level_number: int
    name: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ==================== RACK SLOT (COMPARTMENT) ====================
class RackSlotCreate(BaseModel):
    rack_level_id: str
    slot_number: int
    name: Optional[str] = None


class RackSlotUpdate(BaseModel):
    slot_number: Optional[int] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class RackSlot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rack_level_id: str
    slot_number: int
    name: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ==================== STOCK ITEM ====================
class StockItemCreate(BaseModel):
    warehouse_id: str
    rack_group_id: str
    rack_level_id: str
    rack_slot_id: str
    product_id: str
    variant_id: str  # ZORUNLU - model/variant bazlı stok
    variant_name: Optional[str] = None
    variant_sku: Optional[str] = None
    quantity: float
    min_stock: float = 0
    note: Optional[str] = None
    reference: Optional[str] = None


class StockItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    warehouse_id: str
    rack_group_id: str
    rack_level_id: str
    rack_slot_id: str
    product_id: str
    variant_id: str
    variant_name: Optional[str] = None
    variant_sku: Optional[str] = None
    quantity: float = 0
    reserved_quantity: float = 0  # Teklif rezervasyonu
    min_stock: float = 0
    # Full address for display
    full_address: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# ==================== STOCK MOVEMENT ====================
class StockMovementType:
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    ADJUST = "ADJUST"
    RESERVE = "RESERVE"
    UNRESERVE = "UNRESERVE"


class StockMovementCreate(BaseModel):
    movement_type: str  # IN, OUT, TRANSFER, ADJUST
    warehouse_id: str
    rack_group_id: str
    rack_level_id: str
    rack_slot_id: str
    product_id: str
    variant_id: str
    variant_name: Optional[str] = None
    quantity: float
    # Transfer için hedef
    target_warehouse_id: Optional[str] = None
    target_rack_group_id: Optional[str] = None
    target_rack_level_id: Optional[str] = None
    target_rack_slot_id: Optional[str] = None
    reference: Optional[str] = None
    note: Optional[str] = None


class StockMovement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    movement_type: str
    warehouse_id: str
    rack_group_id: str
    rack_level_id: str
    rack_slot_id: str
    product_id: str
    variant_id: str
    variant_name: Optional[str] = None
    quantity: float
    # Transfer için hedef
    target_warehouse_id: Optional[str] = None
    target_rack_group_id: Optional[str] = None
    target_rack_level_id: Optional[str] = None
    target_rack_slot_id: Optional[str] = None
    # Addresses
    source_address: Optional[str] = None
    target_address: Optional[str] = None
    reference: Optional[str] = None
    note: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


# ==================== INVENTORY COUNT ====================
class InventoryCountCreate(BaseModel):
    warehouse_id: str
    rack_group_id: Optional[str] = None
    rack_level_id: Optional[str] = None
    rack_slot_id: Optional[str] = None
    product_id: str
    variant_id: str
    system_quantity: float
    counted_quantity: float
    note: Optional[str] = None


class InventoryCount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    warehouse_id: str
    rack_group_id: Optional[str] = None
    rack_level_id: Optional[str] = None
    rack_slot_id: Optional[str] = None
    product_id: str
    variant_id: str
    variant_name: Optional[str] = None
    full_address: Optional[str] = None
    system_quantity: float
    counted_quantity: float
    difference: float = 0
    is_approved: bool = False
    note: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    approved_at: Optional[datetime] = None


# ==================== STOCK RESERVATION ====================
class StockReservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quotation_id: str
    quotation_number: str
    product_id: str
    variant_id: str
    variant_name: Optional[str] = None
    warehouse_id: Optional[str] = None  # Belirli depodan rezervasyon
    quantity: float
    status: str = "active"  # active, released, used
    created_at: datetime = Field(default_factory=_now)
    released_at: Optional[datetime] = None
