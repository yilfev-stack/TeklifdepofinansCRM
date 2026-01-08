from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

# ============================================================================
# CUSTOMER MODELS
# ============================================================================

class ContactPerson(BaseModel):
    name: str
    title: Optional[str] = None  # Pozisyon (Satın Alma Müdürü, vs)
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: bool = False  # Ana kontak kişi mi?

class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact_person: Optional[str] = None  # Geriye uyumluluk için
    contacts: List[ContactPerson] = []  # Çoklu kontak kişiler
    email: Optional[str] = None  # Geriye uyumluluk için
    phone: Optional[str] = None  # Geriye uyumluluk için
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Türkiye"
    tax_office: Optional[str] = None
    tax_number: Optional[str] = None
    note: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None  # Geriye uyumluluk
    contacts: List[ContactPerson] = []  # Çoklu kontak
    email: Optional[str] = None  # Geriye uyumluluk
    phone: Optional[str] = None  # Geriye uyumluluk
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Türkiye"
    tax_office: Optional[str] = None
    tax_number: Optional[str] = None
    note: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None  # Geriye uyumluluk
    contacts: Optional[List[ContactPerson]] = None  # Çoklu kontak
    email: Optional[str] = None  # Geriye uyumluluk
    phone: Optional[str] = None  # Geriye uyumluluk
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_office: Optional[str] = None
    tax_number: Optional[str] = None
    note: Optional[str] = None
    is_active: Optional[bool] = None

# ============================================================================
# PRODUCT MODELS
# ============================================================================

class ProductModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str
    sku: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_type: str  # "sales" or "service"
    brand: Optional[str] = None
    model: Optional[str] = None  # Backward compatibility
    models: List[ProductModel] = []  # Multiple models for a brand
    category: Optional[str] = None
    item_short_name: str
    item_description: Optional[str] = None
    default_unit: str = "Adet"
    default_currency: str = "EUR"
    default_unit_price: float = 0.0
    cost_price: Optional[float] = None
    last_used_unit_price: Optional[float] = None
    last_used_currency: Optional[str] = None
    group_id: Optional[str] = None  # Product group ID
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    product_type: str
    brand: Optional[str] = None
    model: Optional[str] = None  # Backward compatibility
    models: List[ProductModel] = []  # Multiple models
    category: Optional[str] = None
    item_short_name: str
    item_description: Optional[str] = None
    default_unit: str = "Adet"
    default_currency: str = "EUR"
    default_unit_price: float = 0.0
    cost_price: Optional[float] = None

class ProductUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None  # Backward compatibility
    models: Optional[List[ProductModel]] = None  # Multiple models
    category: Optional[str] = None
    item_short_name: Optional[str] = None
    item_description: Optional[str] = None
    default_unit: Optional[str] = None
    default_currency: Optional[str] = None
    default_unit_price: Optional[float] = None
    cost_price: Optional[float] = None
    is_active: Optional[bool] = None

# ============================================================================
# LINE ITEM MODELS
# ============================================================================

class LineItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    # Variant/Model support
    variant_id: Optional[str] = None  # model_name from ProductModel
    variant_name: Optional[str] = None  # Display name
    variant_sku: Optional[str] = None  # SKU from ProductModel
    item_short_name: str
    item_description: Optional[str] = None
    line_note: Optional[str] = None
    quantity: float
    unit: str
    currency: str
    unit_price: float
    discount_type: str = "none"  # none | percent | fixed
    discount_value: float = 0.0
    subtotal_before_discount: float = 0.0
    discount_amount: float = 0.0
    line_total: float = 0.0
    cost_price: Optional[float] = None
    margin_amount: Optional[float] = None
    margin_percent: Optional[float] = None
    is_optional: bool = False

class LineItemCreate(BaseModel):
    product_id: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    # Variant/Model support
    variant_id: Optional[str] = None
    variant_name: Optional[str] = None
    variant_sku: Optional[str] = None
    item_short_name: str
    item_description: Optional[str] = None
    line_note: Optional[str] = None
    quantity: float
    unit: str
    currency: str
    unit_price: float
    cost_price: Optional[float] = None
    is_optional: bool = False

# ============================================================================
# QUOTATION MODELS
# ============================================================================

class Quotation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quotation_type: str  # "sales" or "service"
    quote_no: str
    base_quote_no: str
    revision_no: int = 0
    revision_group_id: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    customer_id: str
    customer_name: Optional[str] = None
    customer_details: Optional[dict] = None
    representative_id: Optional[str] = None
    representative_name: Optional[str] = None
    representative_phone: Optional[str] = None
    representative_email: Optional[str] = None
    subject: str
    project_code: Optional[str] = None
    validity_days: int = 30
    delivery_time: Optional[str] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    language: str = "turkish"  # turkish | english
    
    # Status
    offer_status: str = "pending"  # pending | accepted | rejected
    rejection_reason: Optional[str] = None
    invoice_status: str = "none"  # none | waiting_invoice | invoiced
    invoice_number: Optional[str] = None
    is_archived: bool = False
    
    # Delivery status
    delivery_status: Optional[str] = None  # None | "pending" | "delivered"
    delivered_at: Optional[str] = None
    
    # International
    is_international: bool = False
    import_extra_cost_amount: Optional[float] = None
    import_extra_cost_currency: Optional[str] = None
    
    # Shipping
    shipping_term: Optional[str] = None
    
    # Line items
    line_items: List[LineItem] = []
    
    # General Discount (applied to total)
    discount_type: str = "none"  # none | percent | fixed
    discount_value: float = 0.0
    discount_currency: Optional[str] = "EUR"
    
    # Totals (computed)
    totals_by_currency: dict = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Edited PDF
    has_edited_pdf: bool = False
    edited_pdf_path: Optional[str] = None
    edited_pdf_uploaded_at: Optional[str] = None

class QuotationCreate(BaseModel):
    quotation_type: str
    customer_id: str
    representative_id: Optional[str] = None
    subject: str
    project_code: Optional[str] = None
    validity_days: int = 30
    delivery_time: Optional[str] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    language: str = "turkish"
    is_international: bool = False
    import_extra_cost_amount: Optional[float] = None
    import_extra_cost_currency: Optional[str] = None
    shipping_term: Optional[str] = None
    discount_type: str = "none"
    discount_value: float = 0.0
    discount_currency: Optional[str] = "EUR"
    line_items: List[LineItemCreate] = []

class QuotationUpdate(BaseModel):
    customer_id: Optional[str] = None
    representative_id: Optional[str] = None
    subject: Optional[str] = None
    project_code: Optional[str] = None
    validity_days: Optional[int] = None
    delivery_time: Optional[str] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    language: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    discount_currency: Optional[str] = None
    is_international: Optional[bool] = None
    import_extra_cost_amount: Optional[float] = None
    import_extra_cost_currency: Optional[str] = None
    shipping_term: Optional[str] = None
    line_items: Optional[List[LineItemCreate]] = None
    offer_status: Optional[str] = None
    rejection_reason: Optional[str] = None
    invoice_status: Optional[str] = None
    invoice_number: Optional[str] = None
    is_archived: Optional[bool] = None

# ============================================================================
# INTERNAL COST MODELS (SECRET)
# ============================================================================

class CostCategory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    scope: str = "both"  # sales | service | both
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CostCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scope: str = "both"

class InternalCost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quotation_id: str
    category_id: str
    category_name: Optional[str] = None
    description: str
    amount: float
    currency: str
    cost_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InternalCostCreate(BaseModel):
    quotation_id: str
    category_id: str
    description: str
    amount: float
    currency: str
    cost_date: Optional[datetime] = None

# ============================================================================
# REPRESENTATIVE MODELS (DEMART Yetkilisi)
# ============================================================================

class Representative(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RepresentativeCreate(BaseModel):
    name: str
    phone: str
    email: str

class RepresentativeUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None