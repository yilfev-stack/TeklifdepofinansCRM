from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Inventory Categories with their prefixes
INVENTORY_CATEGORIES = {
    "office": {"name": "Ofis Envanteri", "prefix": "D-O"},
    "workshop": {"name": "Atölye Envanteri", "prefix": "D-A"},
    "tools": {"name": "El Aletleri Envanteri", "prefix": "D-EL"},
    "vehicle": {"name": "Araç Envanteri", "prefix": "D-AR"}
}

class InventoryItemCreate(BaseModel):
    category: str  # office, workshop, tools, vehicle
    description: str
    purchase_date: str
    quantity: int = 1
    purchase_price: float = 0.0
    notes: Optional[str] = None

class InventoryItemUpdate(BaseModel):
    description: Optional[str] = None
    purchase_date: Optional[str] = None
    quantity: Optional[int] = None
    purchase_price: Optional[float] = None
    notes: Optional[str] = None
    is_retired: Optional[bool] = None
    retirement_reason: Optional[str] = None

class InventoryItem(BaseModel):
    id: str
    inventory_no: str
    category: str
    description: str
    purchase_date: str
    quantity: int
    purchase_price: float
    notes: Optional[str] = None
    is_retired: bool = False
    retirement_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
