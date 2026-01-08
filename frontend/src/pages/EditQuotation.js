import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ArrowLeft, Plus, Trash2, Save, GitBranch, Lock, FileText, Package, X, Search, Check, FolderOpen, Folder, ChevronDown, ChevronRight, History } from "lucide-react";
import { toast } from "sonner";

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
  { id: "standard", tr: "Standart teslim koşulları", en: "Standard delivery terms" },
  { id: "partial_allowed", tr: "Kısmi sevkiyata izin verilir", en: "Partial shipment allowed" },
  { id: "partial_not_allowed", tr: "Kısmi sevkiyat yapılamaz", en: "Partial shipment not allowed" },
  { id: "standard_packing", tr: "Standart ihracat paketleme", en: "Standard export packing" },
  { id: "buyer_warehouse", tr: "Teslimat: Alıcının deposu / şantiyesi", en: "Delivery: Buyer's warehouse / site" },
  { id: "demart_warehouse", tr: "Teslimat: Demart ofis / depo teslim", en: "Delivery: Delivered to Demart warehouse/office" },
  { id: "custom", tr: "Özel (manuel girilecek)", en: "Custom (manual entry)" }
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
      return isTr ? `${anchorText?.tr || "Fatura tarihinden itibaren"} ${days} gün` : `${days} days ${anchorText?.en || "from invoice date"}`;
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
      return isTr ? `%${advance} Peşin, %${delivery} Teslimatta` : `${advance}% Advance, ${delivery}% on delivery`;
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

// Modal tarzı ürün seçici bileşeni
const ProductSelectorModal = ({ value, onChange, products, productGroups }) => {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedGroups, setExpandedGroups] = useState({});
  
  const getGroupedProducts = () => {
    const grouped = {};
    const ungrouped = [];
    
    const groupMap = {};
    (productGroups || []).forEach(g => {
      groupMap[g.id] = g.name;
      grouped[g.name] = [];
    });
    
    (products || []).forEach(p => {
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
  const selectedProduct = (products || []).find(p => p.id === value);
  
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
      p.brand?.toLowerCase().includes(searchTerm.toLowerCase())
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
          className="w-full justify-between text-left font-normal h-auto min-h-[38px] py-2"
        >
          <span className="truncate text-sm">
            {selectedProduct 
              ? `${selectedProduct.brand ? selectedProduct.brand + ' - ' : ''}${selectedProduct.item_short_name}`
              : 'Manuel giriş'}
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
            <span className="text-base font-medium">Manuel giriş</span>
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
                  {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
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
                        <div className="font-medium text-base">{p.brand ? `${p.brand} - ` : ''}{p.item_short_name}</div>
                        {p.model && <div className="text-sm text-muted-foreground">Model: {p.model}</div>}
                        {p.item_description && <div className="text-sm text-muted-foreground mt-1 line-clamp-2">{p.item_description}</div>}
                      </div>
                      {p.default_unit_price > 0 && (
                        <div className="text-right">
                          <span className="font-semibold text-primary">{p.default_unit_price.toLocaleString('tr-TR')} {p.default_currency}</span>
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
                {expandedGroups['ungrouped'] || searchTerm ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
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
                      <div className="font-medium text-base">{p.brand ? `${p.brand} - ` : ''}{p.item_short_name}</div>
                      {p.model && <div className="text-sm text-muted-foreground">Model: {p.model}</div>}
                      {p.item_description && <div className="text-sm text-muted-foreground mt-1 line-clamp-2">{p.item_description}</div>}
                    </div>
                    {p.default_unit_price > 0 && (
                      <div className="text-right">
                        <span className="font-semibold text-primary">{p.default_unit_price.toLocaleString('tr-TR')} {p.default_currency}</span>
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

const EditQuotation = () => {
  const navigate = useNavigate();
  const { type, id } = useParams();
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [representatives, setRepresentatives] = useState([]);
  const [productGroups, setProductGroups] = useState([]);
  const [customerContacts, setCustomerContacts] = useState([]); // Müşteri yetkilileri
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [revisions, setRevisions] = useState([]);
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  
  const [formData, setFormData] = useState(null);
  const [statusForm, setStatusForm] = useState({
    offer_status: "",
    rejection_reason: "",
    invoice_number: ""
  });

  useEffect(() => {
    fetchQuotation();
    fetchCustomers();
    fetchProducts();
    fetchRepresentatives();
    fetchRevisions();
    fetchProductGroups();
  }, [id]);

  const fetchProductGroups = async () => {
    try {
      const response = await axios.get(`${API}/product-groups`);
      setProductGroups(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error("Error fetching product groups:", error);
    }
  };

  // Müşteri yetkililerini getir
  const fetchCustomerContacts = async (customerId) => {
    if (!customerId) {
      setCustomerContacts([]);
      return;
    }
    try {
      const response = await axios.get(`${API}/customers/${customerId}`);
      setCustomerContacts(response.data.contacts || []);
    } catch (error) {
      console.error("Error fetching customer contacts:", error);
      setCustomerContacts([]);
    }
  };

  const fetchQuotation = async () => {
    try {
      const response = await axios.get(`${API}/quotations/${id}`);
      const data = response.data;
      // Müşteri yetkililerini de getir
      if (data.customer_id) {
        fetchCustomerContacts(data.customer_id);
      }
      setFormData(data);
      setStatusForm({
        offer_status: data.offer_status,
        rejection_reason: data.rejection_reason || "",
        invoice_number: data.invoice_number || ""
      });
    } catch (error) {
      console.error("Error fetching quotation:", error);
      toast.error("Failed to load quotation");
      navigate(`/quotations/${type}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers?is_active=true`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products?product_type=${type}&is_active=true`);
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  };

  const fetchRepresentatives = async () => {
    try {
      const response = await axios.get(`${API}/representatives?is_active=true`);
      setRepresentatives(response.data);
    } catch (error) {
      console.error("Error fetching representatives:", error);
    }
  };

  const fetchRevisions = async () => {
    try {
      const response = await axios.get(`${API}/quotations/${id}/revisions`);
      setRevisions(response.data);
    } catch (error) {
      console.error("Error fetching revisions:", error);
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
        currency: product.default_currency,
        unit_price: product.default_unit_price,
        cost_price: product.cost_price || 0
      };
      setFormData(prev => ({ ...prev, line_items: newItems }));
    } else {
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
        newItems[index] = {
          ...newItems[index],
          variant_id: variant.id || variant.model_name,
          variant_name: variant.model_name,
          variant_sku: variant.sku || "",
          item_short_name: variant.model_name,
          item_description: variant.description || product.item_description || "",
          unit_price: variant.price || product.default_unit_price || 0
        };
        setFormData(prev => ({ ...prev, line_items: newItems }));
      }
    }
  };

  // Seçili ürünün modelleri var mı kontrol et
  const getProductModels = (productId) => {
    const product = products.find(p => p.id === productId);
    return product?.models || [];
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
        currency: "EUR",
        unit_price: 0,
        cost_price: 0,
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
    if (!formData) return {};
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
            `Ara Toplam: ${totalAmount.toFixed(2)} ${formData.discount_currency || 'EUR'}\n` +
            `İndirim: -${discountAmount.toFixed(2)} ${formData.discount_currency || 'EUR'}\n` +
            `Toplam: ${(totalAmount - discountAmount).toFixed(2)} ${formData.discount_currency || 'EUR'}\n\n` +
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
          `Ara Toplam: ${totalAmount.toFixed(2)} ${formData.discount_currency || 'EUR'}\n` +
          `İndirim: -${discountAmount.toFixed(2)} ${formData.discount_currency || 'EUR'}\n` +
          `Toplam: ${(totalAmount - discountAmount).toFixed(2)} ${formData.discount_currency || 'EUR'}\n\n` +
          `İndirim tutarı, ara toplamdan fazla olamaz!\n` +
          `Lütfen indirim değerini düzeltin.`;
        
        alert(errorMsg);
        toast.error("İndirim tutarı hatalı!");
        return;
      }
    }
    
    setSaving(true);
    try {
      await axios.put(`${API}/quotations/${id}`, formData);
      toast.success("Quotation updated successfully");
      navigate(`/quotations/${type}`);
    } catch (error) {
      console.error("Error updating quotation:", error);
      toast.error(error.response?.data?.detail || "Failed to update quotation");
    } finally {
      setSaving(false);
    }
  };

  const handleRevise = async () => {
    if (!window.confirm("Create a new revision? This will duplicate the quotation.")) return;
    
    try {
      const response = await axios.post(`${API}/quotations/${id}/revise`);
      toast.success("Revision created");
      navigate(`/quotations/${type}/edit/${response.data.id}`);
    } catch (error) {
      console.error("Error creating revision:", error);
      toast.error("Failed to create revision");
    }
  };

  const handleStatusUpdate = async () => {
    try {
     await axios.patch(`${API}/quotations/${id}/status`, {
  offer_status: statusForm.offer_status,
  rejection_reason: statusForm.rejection_reason || null,
  invoice_number: statusForm.invoice_number || null
});

      toast.success("Status updated");
      setStatusDialogOpen(false);
      fetchQuotation();
    } catch (error) {
      console.error("Error updating status:", error);
      toast.error("Failed to update status");
    }
  };

  if (loading || !formData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  const totals = calculateTotals();

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(`/quotations/${type}`)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-heading font-bold">Edit Quotation</h1>
                <p className="text-xs text-muted-foreground">{formData.quote_no}</p>
              </div>
            </div>
            
            {/* Consistent Button Order: Revision Dropdown, Add Item, Cancel, Save, New Revision, Update Status, Preview */}
            <div className="flex gap-2">
              {revisions.length > 1 && (
                <select
                  className="px-3 py-2 border rounded bg-background"
                  value={id}
                  onChange={(e) => navigate(`/quotations/${type}/edit/${e.target.value}`)}
                >
                  {revisions.map(rev => (
                    <option key={rev.id} value={rev.id}>
                      {rev.quote_no}
                    </option>
                  ))}
                </select>
              )}
              <Button type="button" onClick={addLineItem} variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Add Item
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate(`/quotations/${type}`)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving} onClick={handleSubmit}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? "Saving..." : "Save"}
              </Button>
              <Button variant="outline" onClick={handleRevise}>
                <GitBranch className="h-4 w-4 mr-2" />
                New Revision
              </Button>
              <Dialog open={statusDialogOpen} onOpenChange={setStatusDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    Update Status
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Update Status</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 mt-4">
                    <div>
                      <Label>Offer Status</Label>
                      <select
                        className="w-full p-2 border rounded bg-background"
                        value={statusForm.offer_status}
                        onChange={(e) => setStatusForm({...statusForm, offer_status: e.target.value})}
                      >
                        <option value="pending">Pending</option>
                        <option value="accepted">Accepted</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </div>
                    {statusForm.offer_status === 'rejected' && (
                      <div>
                        <Label>Rejection Reason</Label>
                        <Textarea
                          value={statusForm.rejection_reason}
                          onChange={(e) => setStatusForm({...statusForm, rejection_reason: e.target.value})}
                          rows={3}
                        />
                      </div>
                    )}
                    {statusForm.offer_status === 'accepted' && (
                      <div>
                        <Label>Invoice Number (optional)</Label>
                        <Input
                          value={statusForm.invoice_number}
                          onChange={(e) => setStatusForm({...statusForm, invoice_number: e.target.value})}
                        />
                      </div>
                    )}
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setStatusDialogOpen(false)}>Cancel</Button>
                      <Button onClick={handleStatusUpdate}>Update</Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
              <Button onClick={() => navigate(`/quotations/${type}/preview/${id}`)}>
                <FileText className="h-4 w-4 mr-2" />
                Preview
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Same structure as CreateQuotation but with edit functionality */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Customer *</Label>
                <select
                  name="customer_id"
                  value={formData.customer_id}
                  onChange={(e) => {
                    const customerId = e.target.value;
                    setFormData(prev => ({ 
                      ...prev, 
                      customer_id: customerId,
                      customer_contact_id: "",
                      customer_contact_name: "",
                      customer_contact_email: "",
                      customer_contact_phone: ""
                    }));
                    fetchCustomerContacts(customerId);
                  }}
                  className="w-full p-2 border rounded bg-background"
                  required
                >
                  {customers.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              
              {/* Müşteri Yetkilisi Dropdown */}
              <div>
                <Label>Müşteri Yetkilisi</Label>
                <select
                  name="customer_contact_id"
                  value={formData.customer_contact_id || ""}
                  onChange={(e) => {
                    const contactId = e.target.value;
                    const contact = customerContacts.find(c => c.id === contactId);
                    setFormData(prev => ({
                      ...prev,
                      customer_contact_id: contactId,
                      customer_contact_name: contact?.name || "",
                      customer_contact_email: contact?.email || "",
                      customer_contact_phone: contact?.phone || ""
                    }));
                  }}
                  className="w-full p-2 border rounded bg-background"
                >
                  <option value="">Yetkili seçin...</option>
                  {customerContacts.map(contact => (
                    <option key={contact.id} value={contact.id}>
                      {contact.name} {contact.phone ? `- ${contact.phone}` : ''}
                    </option>
                  ))}
                </select>
                {formData.customer_contact_name && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {formData.customer_contact_name} 
                    {formData.customer_contact_phone && ` | ${formData.customer_contact_phone}`}
                    {formData.customer_contact_email && ` | ${formData.customer_contact_email}`}
                  </p>
                )}
              </div>

              <div>
                <Label>DEMART Yetkilisi *</Label>
                <select
                  name="representative_id"
                  value={formData.representative_id || ""}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                  required
                >
                  <option value="">DEMART yetkilisi seçin</option>
                  {representatives.map(r => (
                    <option key={r.id} value={r.id}>{r.name} - {r.phone}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Language / Dil *</Label>
                <select
                  name="language"
                  value={formData.language}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background font-semibold"
                >
                  <option value="turkish">🇹🇷 Türkçe</option>
                  <option value="english">🇬🇧 English</option>
                </select>
              </div>
              <div className="col-span-2">
                <Label>Subject *</Label>
                <Input
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label>Project Code</Label>
                <Input
                  name="project_code"
                  value={formData.project_code || ""}
                  onChange={handleInputChange}
                />
              </div>
              <div>
                <Label>Validity (days)</Label>
                <Input
                  type="number"
                  name="validity_days"
                  value={formData.validity_days}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          </Card>

          {/* Line Items - same as CreateQuotation */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Line Items</h2>
              <Button type="button" onClick={addLineItem} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Item
              </Button>
            </div>
            
            <div className="space-y-4">
              {formData.line_items.map((item, index) => (
                <div key={index} className="p-4 bg-background/50 border rounded space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-mono">Item {index + 1}</span>
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
                  
                  <div className="grid grid-cols-12 gap-3">
                    <div className="col-span-3">
                      <Label>Product</Label>
                      <ProductSelectorModal
                        value={item.product_id}
                        onChange={(productId) => handleProductSelect(index, productId)}
                        products={products}
                        productGroups={productGroups}
                      />
                    </div>
                    {/* Model/Variant Dropdown */}
                    <div className="col-span-3">
                      <Label>Model / Variant {getProductModels(item.product_id).length > 0 && <span className="text-red-500">*</span>}</Label>
                      <select
                        value={item.variant_id || ""}
                        onChange={(e) => handleVariantSelect(index, e.target.value)}
                        className={`w-full p-2 border rounded bg-background text-sm ${
                          getProductModels(item.product_id).length > 0 && !item.variant_id 
                            ? 'border-orange-400 bg-orange-50' 
                            : ''
                        }`}
                        disabled={!item.product_id || getProductModels(item.product_id).length === 0}
                      >
                        <option value="">
                          {!item.product_id 
                            ? "Select product first" 
                            : getProductModels(item.product_id).length === 0 
                              ? "No models" 
                              : "Select model..."}
                        </option>
                        {getProductModels(item.product_id).map((m, mIdx) => (
                          <option key={m.id || mIdx} value={m.id || m.model_name}>
                            {m.model_name} {m.sku ? `(${m.sku})` : ''} {m.price ? `- ${m.price}` : ''}
                          </option>
                        ))}
                      </select>
                      {item.variant_sku && (
                        <p className="text-xs text-muted-foreground mt-1">SKU: {item.variant_sku}</p>
                      )}
                      {/* Legacy uyarısı */}
                      {item.product_id && getProductModels(item.product_id).length > 0 && !item.variant_id && (
                        <p className="text-xs text-orange-500 mt-1">⚠️ Model seçilmemiş / Legacy</p>
                      )}
                    </div>
                    <div className="col-span-6">
                      <Label>Item Name</Label>
                      <Input
                        value={item.item_short_name}
                        onChange={(e) => handleLineItemChange(index, 'item_short_name', e.target.value)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>Quantity</Label>
                      <Input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleLineItemChange(index, 'quantity', parseFloat(e.target.value))}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>Unit</Label>
                      <Input
                        value={item.unit}
                        onChange={(e) => handleLineItemChange(index, 'unit', e.target.value)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label>Currency</Label>
                      <select
                        value={item.currency}
                        onChange={(e) => handleLineItemChange(index, 'currency', e.target.value)}
                        className="w-full p-2 border rounded bg-background"
                      >
                        <option value="EUR">EUR</option>
                        <option value="USD">USD</option>
                        <option value="TRY">TRY</option>
                      </select>
                    </div>
                    <div className="col-span-2">
                      <Label>Unit Price</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={item.unit_price}
                        onChange={(e) => handleLineItemChange(index, 'unit_price', parseFloat(e.target.value))}
                      />
                    </div>
                    <div className="col-span-12">
                      <Label>Description</Label>
                      <Textarea
                        value={item.item_description || ""}
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
                        <span className="text-sm">Optional Item</span>
                      </label>
                      <div className="ml-auto text-lg font-bold text-accent">
                        Total: {calculateLineTotal(item).toFixed(2)} {item.currency}
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
                  value={formData.discount_type || "none"}
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
                  value={formData.discount_value || 0}
                  onChange={handleInputChange}
                  disabled={!formData.discount_type || formData.discount_type === 'none'}
                />
              </div>
              <div>
                <Label>Para Birimi</Label>
                <select
                  name="discount_currency"
                  value={formData.discount_currency || "EUR"}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                  disabled={!formData.discount_type || formData.discount_type === 'none'}
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
                      value={formData.import_extra_cost_amount || 0}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <Label>Currency</Label>
                    <select
                      name="import_extra_cost_currency"
                      value={formData.import_extra_cost_currency || "EUR"}
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
                  value={formData.shipping_term || ""}
                  onChange={handleInputChange}
                  className="w-full p-2 border rounded bg-background"
                >
                  <option value="">{formData.language === 'turkish' ? 'Seçiniz...' : 'Select...'}</option>
                  <optgroup label="Incoterms">
                    {INCOTERMS_CODES.map(code => (
                      <option key={code} value={code}>
                        {getShippingTermOptionText(code, formData.language)}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label={formData.language === 'turkish' ? 'Nakliye Ödeme Şekli' : 'Freight Payment'}>
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
            <h2 className="text-xl font-semibold mb-4">Terms & Notes</h2>
            <div className="space-y-4">
              
              {/* DELIVERY TIME - 3 parçalı */}
              <div>
                <Label>Delivery Time</Label>
                <div className="grid grid-cols-4 gap-2 mt-1">
                  <select
                    value={formData.delivery_time_unit || "week"}
                    onChange={(e) => {
                      const newUnit = e.target.value;
                      let newMin = formData.delivery_time_min || 0;
                      let newMax = formData.delivery_time_max || 1;
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
                    <option value="day">{formData.language === 'turkish' ? 'Gün' : 'Day'}</option>
                    <option value="week">{formData.language === 'turkish' ? 'Hafta' : 'Week'}</option>
                  </select>
                  <select
                    value={formData.delivery_time_min || 0}
                    onChange={(e) => {
                      const newMin = parseInt(e.target.value);
                      let newMax = formData.delivery_time_max || 1;
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
                    {Array.from({ length: ((formData.delivery_time_unit || 'week') === 'day' ? 31 : 25) }, (_, i) => (
                      <option key={i} value={i}>{i} min</option>
                    ))}
                  </select>
                  <select
                    value={formData.delivery_time_max || 1}
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
                    {Array.from({ length: ((formData.delivery_time_unit || 'week') === 'day' ? 31 : 25) }, (_, i) => i).filter(i => i >= (formData.delivery_time_min || 0)).map(i => (
                      <option key={i} value={i}>{i} max</option>
                    ))}
                  </select>
                  <div className="p-2 bg-muted rounded text-sm flex items-center">
                    {generateDeliveryTimeText(formData, formData.language)}
                  </div>
                </div>
              </div>

              {/* PAYMENT TERMS - 4 tip */}
              <div>
                <Label>Payment Terms</Label>
                <div className="space-y-2 mt-1">
                  <select
                    value={formData.payment_mode || ""}
                    onChange={(e) => {
                      const mode = e.target.value;
                      const newText = generatePaymentTermsText({ ...formData, payment_mode: mode }, formData.language);
                      setFormData(prev => ({ ...prev, payment_mode: mode, payment_terms: newText }));
                    }}
                    className="w-full p-2 border rounded bg-background"
                  >
                    <option value="">{formData.language === 'turkish' ? 'Ödeme şekli seçin...' : 'Select payment type...'}</option>
                    {PAYMENT_MODE_OPTIONS.map(opt => (
                      <option key={opt.id} value={opt.id}>{formData.language === 'turkish' ? opt.tr : opt.en}</option>
                    ))}
                  </select>

                  {/* Tip 1: Fatura + Gün */}
                  {formData.payment_mode === 'invoice_plus_days' && (
                    <div className="grid grid-cols-2 gap-2">
                      <select
                        value={formData.payment_anchor || "invoice_date"}
                        onChange={(e) => {
                          const anchor = e.target.value;
                          const newText = generatePaymentTermsText({ ...formData, payment_anchor: anchor }, formData.language);
                          setFormData(prev => ({ ...prev, payment_anchor: anchor, payment_terms: newText }));
                        }}
                        className="p-2 border rounded bg-background"
                      >
                        {PAYMENT_ANCHOR_OPTIONS.map(opt => (
                          <option key={opt.id} value={opt.id}>{formData.language === 'turkish' ? opt.tr : opt.en}</option>
                        ))}
                      </select>
                      <Input
                        type="number"
                        min="1"
                        max="365"
                        value={formData.payment_days || 30}
                        onChange={(e) => {
                          const days = parseInt(e.target.value) || 30;
                          const newText = generatePaymentTermsText({ ...formData, payment_days: days }, formData.language);
                          setFormData(prev => ({ ...prev, payment_days: days, payment_terms: newText }));
                        }}
                        placeholder="Gün sayısı"
                      />
                    </div>
                  )}

                  {/* Tip 2: Net Gün */}
                  {formData.payment_mode === 'net_days' && (
                    <Input
                      type="number"
                      min="1"
                      max="365"
                      value={formData.payment_days || 30}
                      onChange={(e) => {
                        const days = parseInt(e.target.value) || 30;
                        const newText = generatePaymentTermsText({ ...formData, payment_days: days }, formData.language);
                        setFormData(prev => ({ ...prev, payment_days: days, payment_terms: newText }));
                      }}
                      placeholder="Net gün sayısı"
                    />
                  )}

                  {/* Tip 3: Kesin Tarih */}
                  {formData.payment_mode === 'exact_date' && (
                    <Input
                      type="date"
                      value={formData.payment_exact_date || ""}
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
                        <Label className="text-xs">{formData.language === 'turkish' ? 'Peşin %' : 'Advance %'}</Label>
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          value={formData.advance_percent || 50}
                          onChange={(e) => {
                            const advance = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
                            const newText = generatePaymentTermsText({ ...formData, advance_percent: advance }, formData.language);
                            setFormData(prev => ({ ...prev, advance_percent: advance, payment_terms: newText }));
                          }}
                        />
                      </div>
                      <div>
                        <Label className="text-xs">{formData.language === 'turkish' ? 'Teslimatta %' : 'On Delivery %'}</Label>
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
                <Label>Delivery Terms</Label>
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
                        <span className="text-sm">{formData.language === 'turkish' ? opt.tr : opt.en}</span>
                      </label>
                    ))}
                  </div>
                  
                  {/* Özel metin alanı (custom seçiliyse) */}
                  {(formData.delivery_terms_selected || []).includes('custom') && (
                    <Textarea
                      value={formData.delivery_terms_custom || ""}
                      onChange={(e) => {
                        const custom = e.target.value;
                        const newText = generateDeliveryTermsText(formData.delivery_terms_selected, custom, formData.language);
                        setFormData(prev => ({ ...prev, delivery_terms_custom: custom, delivery_terms: newText }));
                      }}
                      placeholder={formData.language === 'turkish' ? 'Özel teslimat koşullarını yazın...' : 'Enter custom delivery terms...'}
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
                <Label>Notes</Label>
                <Textarea name="notes" value={formData.notes || ""} onChange={handleInputChange} rows={3} />
              </div>
            </div>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => navigate(`/quotations/${type}`)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving} className="bg-primary">
              <Save className="h-4 w-4 mr-2" />
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditQuotation;
