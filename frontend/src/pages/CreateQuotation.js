import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ArrowLeft, Plus, Trash2, Save, Package, X, History, ChevronDown, ChevronRight, Search, Check, FolderOpen, Folder } from "lucide-react";
import { toast } from "sonner";
import { useTranslation } from "@/i18n/translations";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// INCOTERMS Labels (Kod → Kısa Ad)
const INCOTERMS_LABELS = {
  EXW: { tr: "Üretildiği Tesisten Teslim", en: "Ex Works" },
  FCA: { tr: "Taşıyıcıya Teslim", en: "Free Carrier" },
  FOB: { tr: "Gemide Teslim", en: "Free On Board" },
  CIF: { tr: "Navlun ve Sigorta Dahil", en: "Cost, Insurance & Freight" },
  CPT: { tr: "Taşıma Ücreti Ödenmiş Olarak", en: "Carriage Paid To" },
  DAP: { tr: "Belirlenen Yerde Teslim", en: "Delivered At Place" },
  DDP: { tr: "Gümrük Vergileri Ödenmiş Teslim", en: "Delivered Duty Paid" },
};

// INCOTERMS Descriptions (Kod → Açıklama) - risk kelimesi yok!
const INCOTERMS_DESCRIPTIONS = {
  EXW: {
    tr: "Ürünler satıcının tesisinde hazır edilir. Yükleme, taşıma, sigorta ve lojistik organizasyon alıcı sorumluluğundadır.",
    en: "Goods are made available at the seller's premises. Loading, transportation, insurance and logistics are under the buyer's responsibility."
  },
  FCA: {
    tr: "Satıcı, ürünleri belirlenen yerde taşıyıcıya teslim eder. Ana taşıma, sigorta ve ithalat işlemleri alıcı tarafından organize edilir.",
    en: "Seller delivers the goods to the carrier at the named place. Main carriage, insurance and import arrangements are handled by the buyer."
  },
  FOB: {
    tr: "Satıcı, ürünleri gemiye yükleyene kadar işlemleri yürütür. Yükleme sonrası sorumluluk alıcıya geçer.",
    en: "Seller handles the process until the goods are loaded on board. Responsibilities transfer to the buyer after loading."
  },
  CIF: {
    tr: "Satıcı navlun ve sigortayı karşılar. Yükleme sonrası taşıma süreci alıcı adına devam eder.",
    en: "Seller covers cost, insurance and freight. Transportation continues on behalf of the buyer after loading."
  },
  CPT: {
    tr: "Satıcı taşıma ücretini öder. Ürünler taşıyıcıya teslim edildikten sonra süreç alıcı adına ilerler.",
    en: "Seller pays the carriage. After delivery to the carrier, the process continues on behalf of the buyer."
  },
  DAP: {
    tr: "Satıcı ürünleri belirlenen varış noktasına kadar teslim eder. İthalat vergileri ve gümrük işlemleri alıcıya aittir.",
    en: "Seller delivers the goods to the named destination. Import duties and customs clearance belong to the buyer."
  },
  DDP: {
    tr: "Satıcı tüm taşıma, sigorta ve ithalat süreçlerini üstlenir. Ürünler alıcının belirlenen adresine teslim edilir.",
    en: "Seller handles all transportation, insurance and import processes. Goods are delivered to the buyer's named address."
  }
};

// AO/GO Freight Payment Terms
const FREIGHT_TERMS = {
  AO: {
    trLabel: "A.O — Alıcı Ödemeli",
    enLabel: "A.O — Freight Collect (Buyer Pays)",
    trDesc: "Nakliye ücreti alıcı tarafından ödenir.",
    enDesc: "Freight cost is paid by the buyer."
  },
  GO: {
    trLabel: "G.O — Gönderici Ödemeli",
    enLabel: "G.O — Freight Prepaid (Seller Pays)",
    trDesc: "Nakliye ücreti satıcı tarafından ödenir.",
    enDesc: "Freight cost is paid by the seller."
  }
};

// Tüm Incoterms kodları listesi
const INCOTERMS_CODES = ["EXW", "FCA", "FOB", "CIF", "CPT", "DAP", "DDP"];
const FREIGHT_CODES = ["AO", "GO"];

// Seçilen shipping term için açıklama döndür
const getShippingTermDescription = (term, lang) => {
  if (!term) return "";
  const langKey = lang === "turkish" ? "tr" : "en";
  
  if (INCOTERMS_DESCRIPTIONS[term]) {
    return INCOTERMS_DESCRIPTIONS[term][langKey];
  }
  if (FREIGHT_TERMS[term]) {
    return langKey === "tr" ? FREIGHT_TERMS[term].trDesc : FREIGHT_TERMS[term].enDesc;
  }
  return "";
};

// Dropdown option text oluştur
const getShippingTermOptionText = (code, lang) => {
  const langKey = lang === "turkish" ? "tr" : "en";
  
  if (INCOTERMS_LABELS[code]) {
    return `${code} — ${INCOTERMS_LABELS[code][langKey]}`;
  }
  if (FREIGHT_TERMS[code]) {
    return langKey === "tr" ? FREIGHT_TERMS[code].trLabel : FREIGHT_TERMS[code].enLabel;
  }
  return code;
};

// ========== DELIVERY TERMS DROPDOWN SEÇENEKLERİ ==========
const DELIVERY_TERMS_OPTIONS = [
  {
    id: "standard",
    tr: "Standart teslim koşulları",
    en: "Standard delivery terms"
  },
  {
    id: "partial_allowed",
    tr: "Kısmi sevkiyata izin verilir",
    en: "Partial shipment allowed"
  },
  {
    id: "partial_not_allowed",
    tr: "Kısmi sevkiyat yapılamaz",
    en: "Partial shipment not allowed"
  },
  {
    id: "standard_packing",
    tr: "Standart ihracat paketleme",
    en: "Standard export packing"
  },
  {
    id: "buyer_warehouse",
    tr: "Teslimat: Alıcının deposu / şantiyesi",
    en: "Delivery: Buyer's warehouse / site"
  },
  {
    id: "demart_warehouse",
    tr: "Teslimat: Demart ofis / depo teslim",
    en: "Delivery: Delivered to Demart warehouse/office"
  },
  {
    id: "custom",
    tr: "Özel (manuel girilecek)",
    en: "Custom (manual entry)"
  }
];

// ========== PAYMENT TERMS TİPLERİ ==========
const PAYMENT_MODE_OPTIONS = [
  { id: "invoice_plus_days", tr: "Fatura + Gün", en: "Invoice + Days" },
  { id: "net_days", tr: "Net Gün", en: "Net Days" },
  { id: "exact_date", tr: "Kesin Tarih", en: "Exact Date" },
  { id: "advance_delivery_split", tr: "% Peşin + % Teslimatta", en: "% Advance + % On Delivery" }
];

const PAYMENT_ANCHOR_OPTIONS = [
  { id: "invoice_date", tr: "Fatura tarihinden itibaren", en: "from invoice date" },
  { id: "invoice_issue_date", tr: "Fatura kesim tarihinden itibaren", en: "from invoice issue date" }
];

// Payment Terms metin üretici
const generatePaymentTermsText = (paymentData, lang) => {
  const isTr = lang === "turkish";
  const mode = paymentData.payment_mode;
  
  if (!mode) return "";
  
  switch (mode) {
    case "invoice_plus_days": {
      const days = paymentData.payment_days || 30;
      const anchor = paymentData.payment_anchor || "invoice_date";
      const anchorText = PAYMENT_ANCHOR_OPTIONS.find(a => a.id === anchor);
      if (isTr) {
        return `${anchorText?.tr || "Fatura tarihinden itibaren"} ${days} gün`;
      } else {
        return `${days} days ${anchorText?.en || "from invoice date"}`;
      }
    }
    case "net_days": {
      const days = paymentData.payment_days || 30;
      return isTr ? `Net ${days} gün` : `Net ${days} days`;
    }
    case "exact_date": {
      const date = paymentData.payment_exact_date;
      if (!date) return isTr ? "Ödeme tarihi: -" : "Payment date: -";
      const formatted = new Date(date).toLocaleDateString('tr-TR');
      return isTr ? `Ödeme tarihi: ${formatted}` : `Payment date: ${formatted}`;
    }
    case "advance_delivery_split": {
      const advance = paymentData.advance_percent || 50;
      const delivery = 100 - advance;
      return isTr 
        ? `%${advance} Peşin, %${delivery} Teslimatta`
        : `${advance}% Advance, ${delivery}% on delivery`;
    }
    default:
      return "";
  }
};

// Delivery Time metin üretici
const generateDeliveryTimeText = (deliveryData, lang) => {
  const isTr = lang === "turkish";
  const unit = deliveryData.delivery_time_unit || "week";
  const min = deliveryData.delivery_time_min ?? 0;
  const max = deliveryData.delivery_time_max ?? 1;
  
  if (unit === "day") {
    return isTr ? `${min} - ${max} gün` : `${min} to ${max} days`;
  } else {
    return isTr ? `${min} - ${max} hafta` : `${min} to ${max} week(s)`;
  }
};

// Delivery Terms çoklu seçim metni üretici
const generateDeliveryTermsText = (selectedTerms, customText, lang) => {
  const isTr = lang === "turkish";
  const texts = [];
  
  (selectedTerms || []).forEach(termId => {
    if (termId === "custom" && customText) {
      texts.push(customText);
    } else {
      const option = DELIVERY_TERMS_OPTIONS.find(o => o.id === termId);
      if (option) {
        texts.push(isTr ? option.tr : option.en);
      }
    }
  });
  
  return texts.join("\n");
};

// Modal tarzı ürün seçici bileşeni - %80 tam sayfa boyutunda
const GroupedProductSelector = ({ value, onChange, disabled, products, productGroups, t }) => {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedGroups, setExpandedGroups] = useState({});
  
  // Ürünleri gruplara göre organize et
  const getGroupedProducts = () => {
    const grouped = {};
    const ungrouped = [];
    
    const groupMap = {};
    productGroups.forEach(g => {
      groupMap[g.id] = g.name;
      grouped[g.name] = [];
    });
    
    products.forEach(p => {
      if (p.group_id && groupMap[p.group_id]) {
        grouped[groupMap[p.group_id]].push(p);
      } else {
        ungrouped.push(p);
      }
    });
    
    Object.keys(grouped).forEach(key => {
      if (grouped[key].length === 0) {
        delete grouped[key];
      }
    });
    
    return { grouped, ungrouped };
  };
  
  const { grouped, ungrouped } = getGroupedProducts();
  const selectedProduct = products.find(p => p.id === value);
  
  const toggleGroup = (groupName) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupName]: !prev[groupName]
    }));
  };
  
  const filterProducts = (productList) => {
    if (!searchTerm) return productList;
    return productList.filter(p => 
      p.item_short_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.brand?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.model?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.item_description?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };
  
  const handleSelect = (productId) => {
    onChange(productId);
    setOpen(false);
    setSearchTerm("");
  };
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between text-left font-normal h-auto min-h-[38px] py-2"
          disabled={disabled}
        >
          <span className="truncate">
            {selectedProduct 
              ? `${selectedProduct.brand ? selectedProduct.brand + ' - ' : ''}${selectedProduct.item_short_name}`
              : t('manualEntry')}
          </span>
          <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-[80vw] w-[80vw] max-h-[85vh] h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Package className="h-6 w-6" />
            Ürün Seçimi
          </DialogTitle>
        </DialogHeader>
        
        <div className="border-b pb-3 mb-3">
          <div className="flex items-center gap-2 px-4 py-3 bg-muted rounded-lg">
            <Search className="h-5 w-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Ürün ara... (isim, marka, model, açıklama)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 bg-transparent border-none outline-none text-base"
              autoFocus
            />
            {searchTerm && (
              <X 
                className="h-5 w-5 cursor-pointer text-muted-foreground hover:text-foreground" 
                onClick={() => setSearchTerm("")}
              />
            )}
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto pr-2" style={{ maxHeight: 'calc(80vh - 160px)' }}>
          {/* Manuel Giriş seçeneği */}
          <div
            className={`px-4 py-3 cursor-pointer hover:bg-accent rounded-lg flex items-center gap-3 mb-2 ${!value ? 'bg-accent ring-2 ring-primary' : ''}`}
            onClick={() => handleSelect("")}
          >
            {!value && <Check className="h-5 w-5 text-primary" />}
            <span className="text-base font-medium">{t('manualEntry')}</span>
          </div>
          
          {/* Gruplu ürünler */}
          {Object.entries(grouped).map(([groupName, groupProducts]) => {
            const filteredProducts = filterProducts(groupProducts);
            if (searchTerm && filteredProducts.length === 0) return null;
            
            const isExpanded = expandedGroups[groupName] || !!searchTerm;
            
            return (
              <Collapsible key={groupName} open={isExpanded}>
                <CollapsibleTrigger
                  className="w-full px-4 py-3 flex items-center gap-3 hover:bg-muted cursor-pointer border-t mt-2 rounded-lg"
                  onClick={() => toggleGroup(groupName)}
                >
                  {isExpanded ? (
                    <FolderOpen className="h-5 w-5 text-yellow-500" />
                  ) : (
                    <Folder className="h-5 w-5 text-yellow-500" />
                  )}
                  <span className="font-semibold text-base flex-1 text-left">{groupName}</span>
                  <span className="text-sm text-muted-foreground bg-muted px-2 py-1 rounded">({filteredProducts.length})</span>
                  {isExpanded ? (
                    <ChevronDown className="h-5 w-5" />
                  ) : (
                    <ChevronRight className="h-5 w-5" />
                  )}
                </CollapsibleTrigger>
                <CollapsibleContent>
                  {filteredProducts.map(p => (
                    <div
                      key={p.id}
                      className={`ml-8 px-4 py-3 cursor-pointer hover:bg-accent rounded-lg flex items-start gap-3 border-b border-muted ${value === p.id ? 'bg-accent ring-2 ring-primary' : ''}`}
                      onClick={() => handleSelect(p.id)}
                    >
                      {value === p.id && <Check className="h-5 w-5 text-primary mt-0.5" />}
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-base">
                          {p.brand ? `${p.brand} - ` : ''}{p.item_short_name}
                        </div>
                        {p.model && (
                          <div className="text-sm text-muted-foreground">Model: {p.model}</div>
                        )}
                        {p.item_description && (
                          <div className="text-sm text-muted-foreground mt-1 line-clamp-2">{p.item_description}</div>
                        )}
                      </div>
                      {p.default_unit_price > 0 && (
                        <div className="text-right">
                          <span className="font-semibold text-primary">
                            {p.default_unit_price.toLocaleString('tr-TR')} {p.default_currency}
                          </span>
                          <div className="text-xs text-muted-foreground">{p.default_unit || 'Adet'}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </CollapsibleContent>
              </Collapsible>
            );
          })}
          
          {/* Grupsuz ürünler */}
          {ungrouped.length > 0 && (
            <Collapsible open={expandedGroups['ungrouped'] || !!searchTerm}>
              <CollapsibleTrigger
                className="w-full px-4 py-3 flex items-center gap-3 hover:bg-muted cursor-pointer border-t mt-2 rounded-lg"
                onClick={() => toggleGroup('ungrouped')}
              >
                <Package className="h-5 w-5 text-blue-500" />
                <span className="font-semibold text-base flex-1 text-left">Grupsuz</span>
                <span className="text-sm text-muted-foreground bg-muted px-2 py-1 rounded">({filterProducts(ungrouped).length})</span>
                {expandedGroups['ungrouped'] || searchTerm ? (
                  <ChevronDown className="h-5 w-5" />
                ) : (
                  <ChevronRight className="h-5 w-5" />
                )}
              </CollapsibleTrigger>
              <CollapsibleContent>
                {filterProducts(ungrouped).map(p => (
                  <div
                    key={p.id}
                    className={`ml-8 px-4 py-3 cursor-pointer hover:bg-accent rounded-lg flex items-start gap-3 border-b border-muted ${value === p.id ? 'bg-accent ring-2 ring-primary' : ''}`}
                    onClick={() => handleSelect(p.id)}
                  >
                    {value === p.id && <Check className="h-5 w-5 text-primary mt-0.5" />}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-base">
                        {p.brand ? `${p.brand} - ` : ''}{p.item_short_name}
                      </div>
                      {p.model && (
                        <div className="text-sm text-muted-foreground">Model: {p.model}</div>
                      )}
                      {p.item_description && (
                        <div className="text-sm text-muted-foreground mt-1 line-clamp-2">{p.item_description}</div>
                      )}
                    </div>
                    {p.default_unit_price > 0 && (
                      <div className="text-right">
                        <span className="font-semibold text-primary">
                          {p.default_unit_price.toLocaleString('tr-TR')} {p.default_currency}
                        </span>
                        <div className="text-xs text-muted-foreground">{p.default_unit || 'Adet'}</div>
                      </div>
                    )}
                  </div>
                ))}
              </CollapsibleContent>
            </Collapsible>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

const CreateQuotation = () => {
  const navigate = useNavigate();
  const { type } = useParams();
  const { t, currentLanguage } = useTranslation();
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [representatives, setRepresentatives] = useState([]);
  const [stockData, setStockData] = useState({}); // product_id -> stock info
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [customerContacts, setCustomerContacts] = useState([]); // Seçilen müşterinin yetkilileri
  
  // Yeni Ürün Modal
  const [showNewProductModal, setShowNewProductModal] = useState(false);
  const [savingProduct, setSavingProduct] = useState(false);
  const [newProductData, setNewProductData] = useState({
    brand: "",
    item_short_name: "",
    item_description: "",
    default_unit: "Adet",
    default_currency: "EUR",
    default_unit_price: 0,
    cost_price: 0
  });
  const [productGroups, setProductGroups] = useState([]);
  const [selectedGroupId, setSelectedGroupId] = useState("");
  
  // Fiyat Geçmişi Modal
  const [showPriceHistory, setShowPriceHistory] = useState(false);
  const [priceHistory, setPriceHistory] = useState([]);
  const [priceHistoryLoading, setPriceHistoryLoading] = useState(false);
  const [selectedProductName, setSelectedProductName] = useState("");
  
  const [formData, setFormData] = useState({
    quotation_type: type,
    customer_id: "",
    customer_contact_id: "", // Müşteri yetkilisi
    customer_contact_name: "",
    customer_contact_email: "",
    customer_contact_phone: "",
    representative_id: "",
    subject: "",
    project_code: "",
    validity_days: 30,
    delivery_time: "",
    delivery_terms: "",
    payment_terms: "",
    notes: "",
    language: "turkish",
    is_international: false,
    import_extra_cost_amount: 0,
    import_extra_cost_currency: "TRY",
    shipping_term: "",
    discount_type: "none",
    discount_value: 0,
    discount_currency: "TRY",
    main_currency: "TRY",
    // Yeni Delivery Time alanları
    delivery_time_unit: "week",
    delivery_time_min: 0,
    delivery_time_max: 1,
    // Yeni Payment Terms alanları
    payment_mode: "",
    payment_days: 30,
    payment_exact_date: "",
    advance_percent: 50,
    payment_anchor: "invoice_date",
    // Yeni Delivery Terms alanları (çoklu seçim)
    delivery_terms_selected: [],
    delivery_terms_custom: "",
    line_items: [{
      product_id: "",
      brand: "",
      model: "",
      variant_id: "",
      variant_name: "",
      variant_sku: "",
      item_short_name: "",
      item_description: "",
      line_note: "",
      quantity: 1,
      unit: "Adet",
      currency: "TRY",
      unit_price: 0,
      discount_type: "none",
      discount_value: 0,
      cost_price: 0,
      markup_type: "percent",  // "percent" or "fixed"
      markup_value: 0,
      is_optional: false
    }]
  });

  useEffect(() => {
    fetchCustomers();
    fetchProducts();
    fetchRepresentatives();
    fetchStockData();
    fetchProductGroups();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers?is_active=true`);
      setCustomers(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Error fetching customers:", error);
      setCustomers([]);
    } finally {
      setDataLoading(false);
    }
  };

  const fetchProductGroups = async () => {
    try {
      const response = await axios.get(`${API}/product-groups`);
      setProductGroups(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Error fetching product groups:", error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products?product_type=${type}&is_active=true`);
      setProducts(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Error fetching products:", error);
      setProducts([]);
    }
  };

  const fetchRepresentatives = async () => {
    try {
      const response = await axios.get(`${API}/representatives?is_active=true`);
      setRepresentatives(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Error fetching representatives:", error);
      setRepresentatives([]);
    }
  };

  const fetchStockData = async () => {
    try {
      const response = await axios.get(`${API}/warehouse/stock`);
      const stockByProduct = {};
      response.data.forEach(item => {
        const pid = item.product_id;
        if (!stockByProduct[pid]) {
          stockByProduct[pid] = { total: 0, reserved: 0, available: 0 };
        }
        stockByProduct[pid].total += item.quantity || 0;
        stockByProduct[pid].reserved += item.reserved_quantity || 0;
        stockByProduct[pid].available = stockByProduct[pid].total - stockByProduct[pid].reserved;
      });
      setStockData(stockByProduct);
    } catch (error) {
      console.error("Error fetching stock data:", error);
    }
  };

  // Manuel girilen ürünü ürünlere kaydet
  const saveLineItemAsProduct = async (index) => {
    const item = formData.line_items[index];
    
    if (!item.item_short_name || item.item_short_name.trim() === '') {
      toast.error("Ürün ismi boş olamaz");
      return;
    }
    
    setSavingProduct(true);
    try {
      const productData = {
        product_type: type,
        brand: item.brand || "",
        item_short_name: item.item_short_name,
        item_description: item.item_description || "",
        default_unit: item.unit || "Adet",
        default_currency: item.currency || "EUR",
        default_unit_price: item.unit_price || 0,
        cost_price: item.cost_price || 0,
        is_active: true
      };
      
      const response = await axios.post(`${API}/products`, productData);
      
      // Ürün listesini güncelle
      await fetchProducts();
      
      // Bu satırın product_id'sini güncelle
      const newItems = [...formData.line_items];
      newItems[index].product_id = response.data.id;
      setFormData(prev => ({ ...prev, line_items: newItems }));
      
      toast.success(`"${item.item_short_name}" ürünlere eklendi!`);
    } catch (error) {
      console.error("Error saving product:", error);
      toast.error("Ürün kaydedilemedi");
    } finally {
      setSavingProduct(false);
    }
  };

  // Yeni ürün modalını aç
  const openNewProductModal = () => {
    setNewProductData({
      brand: "",
      item_short_name: "",
      item_description: "",
      default_unit: "Adet",
      default_currency: formData.main_currency || "EUR",
      default_unit_price: 0,
      cost_price: 0
    });
    setSelectedGroupId("");
    setShowNewProductModal(true);
  };

  // Modal'dan yeni ürün oluştur
  const createNewProduct = async () => {
    if (!newProductData.item_short_name || newProductData.item_short_name.trim() === '') {
      toast.error("Ürün ismi zorunlu");
      return;
    }
    
    setSavingProduct(true);
    try {
      const productData = {
        product_type: type,
        brand: newProductData.brand || "",
        item_short_name: newProductData.item_short_name,
        item_description: newProductData.item_description || "",
        default_unit: newProductData.default_unit || "Adet",
        default_currency: newProductData.default_currency || "EUR",
        default_unit_price: parseFloat(newProductData.default_unit_price) || 0,
        cost_price: parseFloat(newProductData.cost_price) || 0,
        group_id: selectedGroupId || null,
        is_active: true
      };
      
      const response = await axios.post(`${API}/products`, productData);
      
      // Ürün listesini güncelle
      await fetchProducts();
      
      toast.success(`"${newProductData.item_short_name}" ürünlere eklendi!`);
      setShowNewProductModal(false);
    } catch (error) {
      console.error("Error creating product:", error);
      toast.error("Ürün oluşturulamadı");
    } finally {
      setSavingProduct(false);
    }
  };

  // Fiyat geçmişini getir
  const fetchPriceHistory = async (productId, productName) => {
    setPriceHistoryLoading(true);
    setSelectedProductName(productName);
    setShowPriceHistory(true);
    
    try {
      const response = await axios.get(`${API}/products/${productId}/price-history?limit=5`);
      setPriceHistory(response.data.history || []);
    } catch (error) {
      console.error("Error fetching price history:", error);
      setPriceHistory([]);
      toast.error("Fiyat geçmişi yüklenemedi");
    } finally {
      setPriceHistoryLoading(false);
    }
  };

  // Tarihi formatla
  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Müşteri seçildiğinde yetkilileri güncelle
  const handleCustomerChange = (e) => {
    const customerId = e.target.value;
    setFormData(prev => ({
      ...prev,
      customer_id: customerId,
      customer_contact_id: "",
      customer_contact_name: "",
      customer_contact_email: "",
      customer_contact_phone: ""
    }));
    
    // Seçilen müşterinin contacts bilgisini al
    const selectedCustomer = customers.find(c => c.id === customerId);
    if (selectedCustomer && selectedCustomer.contacts && selectedCustomer.contacts.length > 0) {
      setCustomerContacts(selectedCustomer.contacts);
    } else {
      setCustomerContacts([]);
    }
  };

  // Müşteri yetkilisi seçildiğinde
  const handleContactChange = (e) => {
    const contactId = e.target.value;
    const contact = customerContacts.find(c => c.id === contactId || c.name === contactId);
    
    if (contact) {
      setFormData(prev => ({
        ...prev,
        customer_contact_id: contact.id || contact.name,
        customer_contact_name: contact.name || "",
        customer_contact_email: contact.email || "",
        customer_contact_phone: contact.phone || ""
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        customer_contact_id: "",
        customer_contact_name: "",
        customer_contact_email: "",
        customer_contact_phone: ""
      }));
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type: inputType, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: inputType === 'checkbox' ? checked : value
    }));
  };

  const handleProductSelect = (index, productId) => {
    const product = products.find(p => p.id === productId);
    if (product) {
      const newItems = [...formData.line_items];
      // Ürün seçildiğinde model/variant bilgilerini sıfırla
      newItems[index] = {
        ...newItems[index],
        product_id: productId,
        brand: product.brand || "",
        model: product.model || "",
        variant_id: "",
        variant_name: "",
        variant_sku: "",
        item_short_name: product.item_short_name,
        item_description: product.item_description || "",
        unit: product.default_unit,
        currency: formData.main_currency,
        unit_price: product.default_unit_price,
        cost_price: product.cost_price || 0
      };
      setFormData(prev => ({ ...prev, line_items: newItems }));
    } else {
      // Manuel giriş - ürün seçimi temizle
      const newItems = [...formData.line_items];
      newItems[index] = {
        ...newItems[index],
        product_id: "",
        brand: "",
        model: "",
        variant_id: "",
        variant_name: "",
        variant_sku: ""
      };
      setFormData(prev => ({ ...prev, line_items: newItems }));
    }
  };

  // Variant/Model seçimi
  const handleVariantSelect = (index, variantId) => {
    const item = formData.line_items[index];
    const product = products.find(p => p.id === item.product_id);
    
    if (product && product.models && product.models.length > 0) {
      const variant = product.models.find(m => m.id === variantId || m.model_name === variantId);
      if (variant) {
        const newItems = [...formData.line_items];
        const costPrice = variant.cost_price || product.cost_price || 0;
        newItems[index] = {
          ...newItems[index],
          variant_id: variant.id || variant.model_name,
          variant_name: variant.model_name,
          variant_sku: variant.sku || "",
          item_short_name: variant.model_name,
          item_description: variant.description || product.item_description || "",
          unit_price: variant.price || product.default_unit_price || 0,
          cost_price: costPrice,
          markup_type: "percent",
          markup_value: 0
        };
        setFormData(prev => ({ ...prev, line_items: newItems }));
      }
    }
  };

  // Kar marjı değiştiğinde satış fiyatını hesapla
  const handleMarkupChange = (index, field, value) => {
    const newItems = [...formData.line_items];
    const item = newItems[index];
    
    if (field === 'markup_type') {
      item.markup_type = value;
    } else if (field === 'markup_value') {
      item.markup_value = parseFloat(value) || 0;
    }
    
    // Satış fiyatını hesapla
    const costPrice = item.cost_price || 0;
    if (costPrice > 0 && item.markup_value > 0) {
      if (item.markup_type === 'percent') {
        item.unit_price = costPrice * (1 + item.markup_value / 100);
      } else {
        item.unit_price = costPrice + item.markup_value;
      }
      // Yuvarla
      item.unit_price = Math.round(item.unit_price * 100) / 100;
    }
    
    setFormData(prev => ({ ...prev, line_items: newItems }));
  };

  // Seçili ürünün modelleri var mı kontrol et
  const getProductModels = (productId) => {
    const product = products.find(p => p.id === productId);
    return product?.models || [];
  };

  // Ürünleri gruplara göre organize et
  const getGroupedProducts = () => {
    const grouped = {};
    const ungrouped = [];
    
    // Grup haritası oluştur
    const groupMap = {};
    productGroups.forEach(g => {
      groupMap[g.id] = g.name;
      grouped[g.name] = [];
    });
    
    // Ürünleri gruplara ayır
    products.forEach(p => {
      if (p.group_id && groupMap[p.group_id]) {
        grouped[groupMap[p.group_id]].push(p);
      } else {
        ungrouped.push(p);
      }
    });
    
    // Boş grupları temizle
    Object.keys(grouped).forEach(key => {
      if (grouped[key].length === 0) {
        delete grouped[key];
      }
    });
    
    return { grouped, ungrouped };
  };

  const handleLineItemChange = (index, field, value) => {
    const newItems = [...formData.line_items];
    newItems[index][field] = value;
    setFormData(prev => ({ ...prev, line_items: newItems }));
  };

  const addLineItem = () => {
    setFormData(prev => ({
      ...prev,
      line_items: [...prev.line_items, {
        product_id: "",
        brand: "",
        model: "",
        variant_id: "",
        variant_name: "",
        variant_sku: "",
        item_short_name: "",
        item_description: "",
        line_note: "",
        quantity: 1,
        unit: "Adet",
        currency: prev.main_currency,
        unit_price: 0,
        discount_type: "none",
        discount_value: 0,
        cost_price: 0,
        markup_type: "percent",
        markup_value: 0,
        is_optional: false
      }]
    }));
  };

  const removeLineItem = (index) => {
    if (formData.line_items.length === 1) {
      toast.error("At least one line item required");
      return;
    }
    setFormData(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index)
    }));
  };

  const calculateLineTotal = (item) => {
    const quantity = parseFloat(item.quantity) || 0;
    const unitPrice = parseFloat(item.unit_price) || 0;
    return quantity * unitPrice;
  };

  const calculateTotals = () => {
    const totals = {};
    formData.line_items.forEach(item => {
      if (!item.is_optional) {
        const currency = item.currency || 'EUR';
        totals[currency] = (totals[currency] || 0) + calculateLineTotal(item);
      }
    });
    return totals;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validasyon: İndirim kontrolü
    if (formData.discount_type !== 'none' && formData.discount_value > 0) {
      const totals = calculateTotals();
      const totalAmount = Object.values(totals).reduce((sum, val) => sum + val, 0);
      
      let discountAmount = 0;
      if (formData.discount_type === 'percent') {
        discountAmount = totalAmount * (formData.discount_value / 100);
        
        // %10 üzeri indirimler için onay
        if (formData.discount_value > 10) {
          const confirmed = window.confirm(
            `⚠️ YÜKSEK İNDİRİM UYARISI ⚠️\n\n` +
            `%${formData.discount_value} indirim uygulamak istediğinizden emin misiniz?\n\n` +
            `Ara Toplam: ${totalAmount.toFixed(2)} ${formData.discount_currency}\n` +
            `İndirim: -${discountAmount.toFixed(2)} ${formData.discount_currency}\n` +
            `Toplam: ${(totalAmount - discountAmount).toFixed(2)} ${formData.discount_currency}\n\n` +
            `Onaylıyor musunuz?`
          );
          if (!confirmed) {
            toast.info("İndirim değerini düzenleyin");
            return;
          }
        }
      } else {
        discountAmount = formData.discount_value;
      }
      
      // Negatif toplam kontrolü
      if (totalAmount - discountAmount < 0) {
        const errorMsg = `❌ HATA: İndirim Çok Yüksek!\n\n` +
          `Ara Toplam: ${totalAmount.toFixed(2)} ${formData.discount_currency}\n` +
          `İndirim: -${discountAmount.toFixed(2)} ${formData.discount_currency}\n` +
          `Toplam: ${(totalAmount - discountAmount).toFixed(2)} ${formData.discount_currency}\n\n` +
          `İndirim tutarı, ara toplamdan fazla olamaz!\n` +
          `Lütfen indirim değerini düzeltin.`;
        
        alert(errorMsg);
        toast.error("İndirim tutarı hatalı!");
        return;
      }
    }
    
    if (!formData.customer_id) {
      toast.error("Please select a customer");
      return;
    }
    
    if (!formData.subject) {
      toast.error("Please enter subject");
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${API}/quotations`, formData);
      toast.success("Quotation created successfully");
      navigate(`/quotations/${type}`);
    } catch (error) {
      console.error("Error creating quotation:", error);
      toast.error(error.response?.data?.detail || "Failed to create quotation");
    } finally {
      setLoading(false);
    }
  };

  const totals = calculateTotals();

  if (dataLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(`/quotations/${type}`)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-heading font-bold">
                  {t('newQuotation')} - {type === 'sales' ? t('salesQuotations') : t('serviceQuotations')}
                </h1>
              </div>
            </div>
            
            {/* Sticky Action Buttons - Consistent Order */}
            <div className="flex gap-2">
              <Button type="button" onClick={addLineItem} variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                {t('addItem')}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate(`/quotations/${type}`)}>
                {t('cancel')}
              </Button>
              <Button type="submit" disabled={loading} onClick={handleSubmit}>
                <Save className="h-4 w-4 mr-2" />
                {loading ? t('saving') : t('save')}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">{t('customer')} & {t('subject')}</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>{t('customer')} *</Label>
                <select
                  name="customer_id"
                  value={formData.customer_id}
                  onChange={handleCustomerChange}
                  className="w-full p-2 border rounded bg-background"
                  required
                  disabled={!Array.isArray(customers) || customers.length === 0}
                >
                  <option value="">
                    {!Array.isArray(customers) || customers.length === 0 
                      ? t('noCustomersFound')
                      : t('selectCustomer')}
                  </option>
                  {Array.isArray(customers) && customers.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Müşteri Yetkilisi</Label>
                <select
                  name="customer_contact_id"
                  value={formData.customer_contact_id}
                  onChange={handleContactChange}
                  className="w-full p-2 border rounded bg-background"
                  disabled={customerContacts.length === 0}
                >
                  <option value="">
                    {customerContacts.length === 0 
                      ? "Önce müşteri seçin"
                      : "Yetkili seçin..."}
                  </option>
                  {customerContacts.map((contact, idx) => (
                    <option key={contact.id || idx} value={contact.id || contact.name}>
                      {contact.name} {contact.title ? `(${contact.title})` : ""} - {contact.phone || contact.email || ""}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label>{t('demartRepresentatives')} *</Label>
                <select
                  name="representative_id"
                  value={formData.representative_id}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                  required
                  disabled={!Array.isArray(representatives) || representatives.length === 0}
                >
                  <option value="">
                    {!Array.isArray(representatives) || representatives.length === 0
                      ? t('noCustomersFound')
                      : t('selectRepresentative')}
                  </option>
                  {Array.isArray(representatives) && representatives.map(r => (
                    <option key={r.id} value={r.id}>{r.name} - {r.phone}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>{t('language')} *</Label>
                <select
                  name="language"
                  value={formData.language}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background font-semibold"
                >
                  <option value="turkish">🇹🇷 {t('turkish')}</option>
                  <option value="english">🇬🇧 {t('english')}</option>
                </select>
              </div>
              <div className="col-span-2">
                <Label>{t('subject')} *</Label>
                <Input
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label>{t('projectCode')}</Label>
                <Input
                  name="project_code"
                  value={formData.project_code}
                  onChange={handleInputChange}
                />
              </div>
              <div>
                <Label>{t('validity')} ({t('days')})</Label>
                <Input
                  type="number"
                  name="validity_days"
                  value={formData.validity_days}
                  onChange={handleInputChange}
                />
              </div>
              <div>
                <Label>{t('mainCurrency')} *</Label>
                <select
                  name="main_currency"
                  value={formData.main_currency}
                  onChange={(e) => {
                    const newCurrency = e.target.value;
                    const updatedLineItems = formData.line_items.map(item => ({
                      ...item,
                      currency: newCurrency
                    }));
                    setFormData({
                      ...formData,
                      main_currency: newCurrency,
                      discount_currency: newCurrency,
                      import_extra_cost_currency: newCurrency,
                      line_items: updatedLineItems
                    });
                  }}
                  className="w-full p-2 border rounded bg-background"
                  required
                >
                  <option value="TRY">🇹🇷 TRY (Türk Lirası)</option>
                  <option value="EUR">🇪🇺 EUR (Euro)</option>
                  <option value="USD">🇺🇸 USD (Dolar)</option>
                </select>
                <p className="text-xs text-muted-foreground mt-1">
                  {t('currentLanguage') === 'tr' ? 'Tüm kalemler bu para biriminde olacaktır' : 'All line items will be in this currency'}
                </p>
              </div>
            </div>
          </Card>

          {/* Line Items */}
          <Card className="p-6">
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold">{t('lineItems')}</h2>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={openNewProductModal}
              >
                <Package className="h-4 w-4 mr-2" />
                Yeni Ürün Oluştur
              </Button>
            </div>
            
            <div className="space-y-4">
              {formData.line_items.map((item, index) => (
                <div key={index} className="p-4 bg-background/50 border rounded space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-mono">{currentLanguage === 'tr' ? 'Kalem' : 'Item'} {index + 1}</span>
                    <div className="flex items-center gap-2">
                      {/* Manuel giriş ise "Ürünlere Ekle" butonu göster */}
                      {!item.product_id && item.item_short_name && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => saveLineItemAsProduct(index)}
                          disabled={savingProduct}
                          title="Bu ürünü ürün listesine kaydet"
                        >
                          <Package className="h-4 w-4 mr-1" />
                          {savingProduct ? "..." : "Ürünlere Ekle"}
                        </Button>
                      )}
                      {formData.line_items.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeLineItem(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-12 gap-3">
                    <div className="col-span-3">
                      <Label>{t('products')}</Label>
                      <GroupedProductSelector
                        value={item.product_id}
                        onChange={(productId) => handleProductSelect(index, productId)}
                        disabled={!Array.isArray(products) || products.length === 0}
                        products={products}
                        productGroups={productGroups}
                        t={t}
                      />
                      {/* Fiyat Geçmişi Butonu */}
                      {item.product_id && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="mt-1 text-xs h-6 px-2"
                          onClick={() => {
                            const product = products.find(p => p.id === item.product_id);
                            fetchPriceHistory(item.product_id, product?.item_short_name || "Ürün");
                          }}
                          title="Fiyat geçmişini gör"
                        >
                          <History className="h-3 w-3 mr-1" />
                          Fiyat Geçmişi
                        </Button>
                      )}
                    </div>
                    {/* Model/Variant Dropdown - sadece ürünün modelleri varsa göster */}
                    <div className="col-span-3">
                      <Label>Model / Variant {getProductModels(item.product_id).length > 0 && <span className="text-red-500">*</span>}</Label>
                      <select
                        value={item.variant_id || ""}
                        onChange={(e) => handleVariantSelect(index, e.target.value)}
                        className={`w-full p-2 border rounded text-sm ${
                          !item.product_id || getProductModels(item.product_id).length === 0
                            ? 'bg-gray-100 dark:bg-gray-800 text-gray-500'
                            : getProductModels(item.product_id).length > 0 && !item.variant_id 
                              ? 'border-orange-400 bg-orange-50 dark:bg-orange-950 text-orange-800 dark:text-orange-200' 
                              : 'bg-background'
                        }`}
                        disabled={!item.product_id || getProductModels(item.product_id).length === 0}
                      >
                        <option value="">
                          {!item.product_id 
                            ? "Önce ürün seçin" 
                            : getProductModels(item.product_id).length === 0 
                              ? "Model yok" 
                              : "⚠️ Model seçin..."}
                        </option>
                        {getProductModels(item.product_id).map((m, mIdx) => (
                          <option key={m.id || mIdx} value={m.id || m.model_name}>
                            {m.model_name} {m.sku ? `(${m.sku})` : ''} {m.price ? `- ${m.price} ${formData.main_currency}` : ''}
                          </option>
                        ))}
                      </select>
                      {item.variant_sku && (
                        <p className="text-xs text-muted-foreground mt-1">SKU: {item.variant_sku}</p>
                      )}
                      {/* Stock Info Badge */}
                      {item.product_id && (
                        <div className={`mt-1 text-xs px-2 py-1 rounded inline-block ${
                          stockData[item.product_id]?.available > 0 
                            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                            : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                        }`}>
                          📦 {stockData[item.product_id] 
                            ? `Stok: ${stockData[item.product_id].available} adet${stockData[item.product_id].reserved > 0 ? ` (${stockData[item.product_id].reserved} rezerve)` : ''}`
                            : 'Stokta yok'}
                        </div>
                      )}
                    </div>
                    <div className="col-span-6">
                      <Label>{t('itemName')}</Label>
                      <Input
                        value={item.item_short_name}
                        onChange={(e) => handleLineItemChange(index, 'item_short_name', e.target.value)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>{t('quantity')}</Label>
                      <Input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleLineItemChange(index, 'quantity', parseFloat(e.target.value))}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>{t('unit')}</Label>
                      <Input
                        value={item.unit}
                        onChange={(e) => handleLineItemChange(index, 'unit', e.target.value)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>{t('currency')}</Label>
                      <Input
                        value={formData.main_currency}
                        disabled
                        className="w-full p-2 border rounded bg-muted cursor-not-allowed"
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>{t('unitPrice')}</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={item.unit_price}
                        onChange={(e) => handleLineItemChange(index, 'unit_price', parseFloat(e.target.value))}
                      />
                    </div>
                    
                    {/* Kar Marjı Bölümü - Sadece cost_price varsa göster */}
                    {item.cost_price > 0 && (
                      <div className="col-span-12 mt-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-800">
                        <div className="flex items-center gap-4 flex-wrap">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-yellow-700 dark:text-yellow-400">💰 Alış:</span>
                            <span className="font-bold text-yellow-700 dark:text-yellow-400">{item.cost_price.toFixed(2)} {item.currency}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm">Kar:</span>
                            <select
                              value={item.markup_type || 'percent'}
                              onChange={(e) => handleMarkupChange(index, 'markup_type', e.target.value)}
                              className="p-1 border rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                            >
                              <option value="percent">%</option>
                              <option value="fixed">+Sabit</option>
                            </select>
                            <input
                              type="number"
                              step="0.01"
                              className="w-20 h-8 px-2 border rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600"
                              value={item.markup_value || 0}
                              onChange={(e) => handleMarkupChange(index, 'markup_value', e.target.value)}
                              placeholder={item.markup_type === 'percent' ? '%' : '+'}
                            />
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-green-700 dark:text-green-400">➡️ Satış:</span>
                            <span className="font-bold text-green-700 dark:text-green-400">{item.unit_price.toFixed(2)} {item.currency}</span>
                          </div>
                          {item.markup_value > 0 && (
                            <div className="text-xs text-muted-foreground">
                              (Kar: {item.markup_type === 'percent' 
                                ? `%${item.markup_value}` 
                                : `+${item.markup_value} ${item.currency}`} = {(item.unit_price - item.cost_price).toFixed(2)} {item.currency})
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="col-span-12">
                      <Label>{t('description')}</Label>
                      <Textarea
                        value={item.item_description}
                        onChange={(e) => handleLineItemChange(index, 'item_description', e.target.value)}
                        rows={2}
                      />
                    </div>
                    <div className="col-span-12 flex items-center gap-4">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={item.is_optional}
                          onChange={(e) => handleLineItemChange(index, 'is_optional', e.target.checked)}
                        />
                        <span className="text-sm">{t('optional')}</span>
                      </label>
                      <div className="ml-auto text-lg font-bold text-accent">
                        {t('total')}: {calculateLineTotal(item).toFixed(2)} {item.currency}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-4 border-t">
              <div className="text-right space-y-2">
                {Object.keys(totals).map(currency => (
                  <div key={currency} className="text-xl font-bold text-accent">
                    Total: {totals[currency].toFixed(2)} {currency}
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* General Discount */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Genel İndirim (Toplam Üzerinden)</h2>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>İndirim Tipi</Label>
                <select
                  name="discount_type"
                  value={formData.discount_type}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                >
                  <option value="none">İndirim Yok</option>
                  <option value="percent">Yüzde (%)</option>
                  <option value="fixed">Sabit Tutar</option>
                </select>
              </div>
              <div>
                <Label>İndirim Değeri</Label>
                <Input
                  type="number"
                  step="0.01"
                  name="discount_value"
                  value={formData.discount_value}
                  onChange={handleInputChange}
                  disabled={formData.discount_type === 'none'}
                />
              </div>
              <div>
                <Label>Para Birimi</Label>
                <select
                  name="discount_currency"
                  value={formData.discount_currency}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                  disabled={formData.discount_type === 'none'}
                >
                  <option value="EUR">EUR</option>
                  <option value="USD">USD</option>
                  <option value="TRY">TRY</option>
                </select>
              </div>
            </div>
          </Card>

          {/* International & Shipping */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">International & Shipping</h2>
            <div className="space-y-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="is_international"
                  checked={formData.is_international}
                  onChange={handleInputChange}
                />
                <span>International Order</span>
              </label>
              
              {formData.is_international && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Import/Freight/Customs Cost</Label>
                    <Input
                      type="number"
                      step="0.01"
                      name="import_extra_cost_amount"
                      value={formData.import_extra_cost_amount}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <Label>Currency</Label>
                    <select
                      name="import_extra_cost_currency"
                      value={formData.import_extra_cost_currency}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded bg-background"
                    >
                      <option value="EUR">EUR</option>
                      <option value="USD">USD</option>
                      <option value="TRY">TRY</option>
                    </select>
                  </div>
                </div>
              )}
              
              <div>
                <Label>Shipping Terms (Incoterms)</Label>
                <select
                  name="shipping_term"
                  value={formData.shipping_term}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                >
                  <option value="">{currentLanguage === 'tr' ? 'Seçiniz...' : 'Select...'}</option>
                  <optgroup label={currentLanguage === 'tr' ? 'Incoterms' : 'Incoterms'}>
                    {INCOTERMS_CODES.map(code => (
                      <option key={code} value={code}>
                        {getShippingTermOptionText(code, formData.language)}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label={currentLanguage === 'tr' ? 'Nakliye Ödeme Şekli' : 'Freight Payment'}>
                    {FREIGHT_CODES.map(code => (
                      <option key={code} value={code}>
                        {getShippingTermOptionText(code, formData.language)}
                      </option>
                    ))}
                  </optgroup>
                </select>
                {/* Seçilen shipping term için açıklama */}
                {formData.shipping_term && (
                  <p className="text-xs text-muted-foreground mt-2 p-2 bg-muted/50 rounded border-l-2 border-primary">
                    {getShippingTermDescription(formData.shipping_term, formData.language)}
                  </p>
                )}
              </div>
            </div>
          </Card>

          {/* Terms & Notes */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">{currentLanguage === 'tr' ? 'Şartlar ve Notlar' : 'Terms & Notes'}</h2>
            <div className="space-y-4">
              
              {/* DELIVERY TIME - 3 parçalı */}
              <div>
                <Label>{t('deliveryTime')}</Label>
                <div className="grid grid-cols-4 gap-2 mt-1">
                  <select
                    value={formData.delivery_time_unit}
                    onChange={(e) => {
                      const newUnit = e.target.value;
                      let newMin = formData.delivery_time_min;
                      let newMax = formData.delivery_time_max;
                      // Birim değişince sınırları kontrol et
                      const maxLimit = newUnit === 'day' ? 30 : 24;
                      if (newMin > maxLimit) newMin = maxLimit;
                      if (newMax > maxLimit) newMax = maxLimit;
                      if (newMax < newMin) newMax = newMin;
                      setFormData(prev => ({
                        ...prev,
                        delivery_time_unit: newUnit,
                        delivery_time_min: newMin,
                        delivery_time_max: newMax,
                        delivery_time: generateDeliveryTimeText({ delivery_time_unit: newUnit, delivery_time_min: newMin, delivery_time_max: newMax }, prev.language)
                      }));
                    }}
                    className="p-2 border rounded bg-background"
                  >
                    <option value="day">{currentLanguage === 'tr' ? 'Gün' : 'Day'}</option>
                    <option value="week">{currentLanguage === 'tr' ? 'Hafta' : 'Week'}</option>
                  </select>
                  <select
                    value={formData.delivery_time_min}
                    onChange={(e) => {
                      const newMin = parseInt(e.target.value);
                      let newMax = formData.delivery_time_max;
                      if (newMax < newMin) newMax = newMin;
                      setFormData(prev => ({
                        ...prev,
                        delivery_time_min: newMin,
                        delivery_time_max: newMax,
                        delivery_time: generateDeliveryTimeText({ ...prev, delivery_time_min: newMin, delivery_time_max: newMax }, prev.language)
                      }));
                    }}
                    className="p-2 border rounded bg-background"
                  >
                    {Array.from({ length: (formData.delivery_time_unit === 'day' ? 31 : 25) }, (_, i) => (
                      <option key={i} value={i}>{i} {currentLanguage === 'tr' ? 'min' : 'min'}</option>
                    ))}
                  </select>
                  <select
                    value={formData.delivery_time_max}
                    onChange={(e) => {
                      const newMax = parseInt(e.target.value);
                      setFormData(prev => ({
                        ...prev,
                        delivery_time_max: newMax,
                        delivery_time: generateDeliveryTimeText({ ...prev, delivery_time_max: newMax }, prev.language)
                      }));
                    }}
                    className="p-2 border rounded bg-background"
                  >
                    {Array.from({ length: (formData.delivery_time_unit === 'day' ? 31 : 25) }, (_, i) => i).filter(i => i >= formData.delivery_time_min).map(i => (
                      <option key={i} value={i}>{i} {currentLanguage === 'tr' ? 'max' : 'max'}</option>
                    ))}
                  </select>
                  <div className="p-2 bg-muted rounded text-sm flex items-center">
                    {generateDeliveryTimeText(formData, formData.language)}
                  </div>
                </div>
              </div>

              {/* PAYMENT TERMS - 4 tip */}
              <div>
                <Label>{t('paymentTerms')}</Label>
                <div className="space-y-2 mt-1">
                  <select
                    value={formData.payment_mode}
                    onChange={(e) => {
                      const mode = e.target.value;
                      const newText = generatePaymentTermsText({ ...formData, payment_mode: mode }, formData.language);
                      setFormData(prev => ({ ...prev, payment_mode: mode, payment_terms: newText }));
                    }}
                    className="w-full p-2 border rounded bg-background"
                  >
                    <option value="">{currentLanguage === 'tr' ? 'Ödeme şekli seçin...' : 'Select payment type...'}</option>
                    {PAYMENT_MODE_OPTIONS.map(opt => (
                      <option key={opt.id} value={opt.id}>{currentLanguage === 'tr' ? opt.tr : opt.en}</option>
                    ))}
                  </select>

                  {/* Tip 1: Fatura + Gün */}
                  {formData.payment_mode === 'invoice_plus_days' && (
                    <div className="grid grid-cols-2 gap-2">
                      <select
                        value={formData.payment_anchor}
                        onChange={(e) => {
                          const anchor = e.target.value;
                          const newText = generatePaymentTermsText({ ...formData, payment_anchor: anchor }, formData.language);
                          setFormData(prev => ({ ...prev, payment_anchor: anchor, payment_terms: newText }));
                        }}
                        className="p-2 border rounded bg-background"
                      >
                        {PAYMENT_ANCHOR_OPTIONS.map(opt => (
                          <option key={opt.id} value={opt.id}>{currentLanguage === 'tr' ? opt.tr : opt.en}</option>
                        ))}
                      </select>
                      <Input
                        type="number"
                        min="1"
                        max="365"
                        value={formData.payment_days}
                        onChange={(e) => {
                          const days = parseInt(e.target.value) || 30;
                          const newText = generatePaymentTermsText({ ...formData, payment_days: days }, formData.language);
                          setFormData(prev => ({ ...prev, payment_days: days, payment_terms: newText }));
                        }}
                        placeholder={currentLanguage === 'tr' ? 'Gün sayısı' : 'Days'}
                      />
                    </div>
                  )}

                  {/* Tip 2: Net Gün */}
                  {formData.payment_mode === 'net_days' && (
                    <Input
                      type="number"
                      min="1"
                      max="365"
                      value={formData.payment_days}
                      onChange={(e) => {
                        const days = parseInt(e.target.value) || 30;
                        const newText = generatePaymentTermsText({ ...formData, payment_days: days }, formData.language);
                        setFormData(prev => ({ ...prev, payment_days: days, payment_terms: newText }));
                      }}
                      placeholder={currentLanguage === 'tr' ? 'Net gün sayısı' : 'Net days'}
                    />
                  )}

                  {/* Tip 3: Kesin Tarih */}
                  {formData.payment_mode === 'exact_date' && (
                    <Input
                      type="date"
                      value={formData.payment_exact_date}
                      onChange={(e) => {
                        const date = e.target.value;
                        const newText = generatePaymentTermsText({ ...formData, payment_exact_date: date }, formData.language);
                        setFormData(prev => ({ ...prev, payment_exact_date: date, payment_terms: newText }));
                      }}
                    />
                  )}

                  {/* Tip 4: % Peşin + % Teslimatta */}
                  {formData.payment_mode === 'advance_delivery_split' && (
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label className="text-xs">{currentLanguage === 'tr' ? 'Peşin %' : 'Advance %'}</Label>
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          value={formData.advance_percent}
                          onChange={(e) => {
                            const advance = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
                            const newText = generatePaymentTermsText({ ...formData, advance_percent: advance }, formData.language);
                            setFormData(prev => ({ ...prev, advance_percent: advance, payment_terms: newText }));
                          }}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">{currentLanguage === 'tr' ? 'Teslimatta %' : 'On Delivery %'}</Label>
                        <Input type="number" value={100 - (formData.advance_percent || 0)} disabled className="bg-muted" />
                      </div>
                    </div>
                  )}

                  {/* Üretilen metin */}
                  {formData.payment_mode && (
                    <div className="p-2 bg-muted rounded text-sm border-l-2 border-primary">
                      {generatePaymentTermsText(formData, formData.language)}
                    </div>
                  )}
                </div>
              </div>

              {/* DELIVERY TERMS - Çoklu seçim */}
              <div>
                <Label>{t('deliveryTerms')}</Label>
                <div className="space-y-2 mt-1">
                  <div className="grid grid-cols-2 gap-2">
                    {DELIVERY_TERMS_OPTIONS.map(opt => (
                      <label key={opt.id} className="flex items-center gap-2 p-2 border rounded hover:bg-accent cursor-pointer">
                        <input
                          type="checkbox"
                          checked={(formData.delivery_terms_selected || []).includes(opt.id)}
                          onChange={(e) => {
                            const selected = formData.delivery_terms_selected || [];
                            let newSelected;
                            if (e.target.checked) {
                              newSelected = [...selected, opt.id];
                            } else {
                              newSelected = selected.filter(id => id !== opt.id);
                            }
                            const newText = generateDeliveryTermsText(newSelected, formData.delivery_terms_custom, formData.language);
                            setFormData(prev => ({ ...prev, delivery_terms_selected: newSelected, delivery_terms: newText }));
                          }}
                          className="w-4 h-4"
                        />
                        <span className="text-sm">{currentLanguage === 'tr' ? opt.tr : opt.en}</span>
                      </label>
                    ))}
                  </div>
                  
                  {/* Özel metin alanı (custom seçiliyse) */}
                  {(formData.delivery_terms_selected || []).includes('custom') && (
                    <Textarea
                      value={formData.delivery_terms_custom}
                      onChange={(e) => {
                        const custom = e.target.value;
                        const newText = generateDeliveryTermsText(formData.delivery_terms_selected, custom, formData.language);
                        setFormData(prev => ({ ...prev, delivery_terms_custom: custom, delivery_terms: newText }));
                      }}
                      placeholder={currentLanguage === 'tr' ? 'Özel teslimat koşullarını yazın...' : 'Enter custom delivery terms...'}
                      rows={2}
                    />
                  )}

                  {/* Seçilen koşulların önizlemesi */}
                  {(formData.delivery_terms_selected || []).length > 0 && (
                    <div className="p-2 bg-muted rounded text-sm border-l-2 border-primary whitespace-pre-line">
                      {generateDeliveryTermsText(formData.delivery_terms_selected, formData.delivery_terms_custom, formData.language)}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <Label>{t('notes')}</Label>
                <Textarea name="notes" value={formData.notes} onChange={handleInputChange} rows={3} />
              </div>
            </div>
          </Card>

        </form>
      </div>

      {/* Yeni Ürün Modal */}
      {showNewProductModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-lg shadow-xl w-full max-w-lg">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Package className="h-5 w-5" />
                Yeni Ürün Oluştur
              </h3>
              <Button variant="ghost" size="icon" onClick={() => setShowNewProductModal(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Marka</Label>
                  <Input
                    value={newProductData.brand}
                    onChange={(e) => setNewProductData(prev => ({ ...prev, brand: e.target.value }))}
                    placeholder="Örn: SOFIS"
                  />
                </div>
                <div>
                  <Label>Grup</Label>
                  <select
                    value={selectedGroupId}
                    onChange={(e) => setSelectedGroupId(e.target.value)}
                    className="w-full p-2 border rounded bg-background"
                  >
                    <option value="">Grupsuz</option>
                    {productGroups.map(g => (
                      <option key={g.id} value={g.id}>{g.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div>
                <Label>Ürün Adı *</Label>
                <Input
                  value={newProductData.item_short_name}
                  onChange={(e) => setNewProductData(prev => ({ ...prev, item_short_name: e.target.value }))}
                  placeholder="Ürün adını girin..."
                  required
                />
              </div>
              
              <div>
                <Label>Açıklama</Label>
                <Textarea
                  value={newProductData.item_description}
                  onChange={(e) => setNewProductData(prev => ({ ...prev, item_description: e.target.value }))}
                  rows={2}
                  placeholder="Ürün açıklaması..."
                />
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>Birim</Label>
                  <select
                    value={newProductData.default_unit}
                    onChange={(e) => setNewProductData(prev => ({ ...prev, default_unit: e.target.value }))}
                    className="w-full p-2 border rounded bg-background"
                  >
                    <option value="Adet">Adet</option>
                    <option value="Set">Set</option>
                    <option value="Paket">Paket</option>
                    <option value="Metre">Metre</option>
                    <option value="Kg">Kg</option>
                  </select>
                </div>
                <div>
                  <Label>Para Birimi</Label>
                  <select
                    value={newProductData.default_currency}
                    onChange={(e) => setNewProductData(prev => ({ ...prev, default_currency: e.target.value }))}
                    className="w-full p-2 border rounded bg-background"
                  >
                    <option value="EUR">EUR</option>
                    <option value="USD">USD</option>
                    <option value="TRY">TRY</option>
                  </select>
                </div>
                <div>
                  <Label>Maliyet Fiyatı</Label>
                  <Input
                    type="number"
                    value={newProductData.cost_price}
                    onChange={(e) => setNewProductData(prev => ({ ...prev, cost_price: e.target.value }))}
                    step="0.01"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 p-4 border-t">
              <Button variant="outline" onClick={() => setShowNewProductModal(false)}>
                İptal
              </Button>
              <Button onClick={createNewProduct} disabled={savingProduct || !newProductData.item_short_name}>
                {savingProduct ? "Kaydediliyor..." : "Ürün Oluştur"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Fiyat Geçmişi Modal */}
      {showPriceHistory && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-background rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <History className="h-5 w-5 text-blue-500" />
                Fiyat Geçmişi - {selectedProductName}
              </h3>
              <Button variant="ghost" size="icon" onClick={() => setShowPriceHistory(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {priceHistoryLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Yükleniyor...
                </div>
              ) : priceHistory.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <History className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Bu ürün için fiyat geçmişi bulunamadı.</p>
                  <p className="text-sm">Henüz hiçbir teklifte kullanılmamış.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground mb-4">
                    Son {priceHistory.length} teklifte verilen fiyatlar:
                  </p>
                  {priceHistory.map((h, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-muted/30 rounded-lg border">
                      <div className="flex-1">
                        <div className="font-medium">{h.customer_name}</div>
                        <div className="text-sm text-muted-foreground">
                          {h.quotation_number && <span className="mr-2">#{h.quotation_number}</span>}
                          {formatDate(h.date)}
                          {h.variant_name && <span className="ml-2 text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{h.variant_name}</span>}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                          {new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(h.unit_price)} {h.currency}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {h.quantity > 1 && `${h.quantity} adet`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="flex justify-end p-4 border-t">
              <Button variant="outline" onClick={() => setShowPriceHistory(false)}>
                Kapat
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateQuotation;