// BASİT ÇEVİRİ SİSTEMİ
// KURAL: Kullanıcının yazdığı veri → DEĞİŞMEZ
// KURAL: UI metinleri (label, button, başlık) → DİLE GÖRE DEĞİŞİR

export const translations = {
  tr: {
    // Common
    save: "Kaydet",
    cancel: "İptal",
    edit: "Düzenle",
    delete: "Sil",
    add: "Ekle",

    // Customers
    customers: "Müşteriler",
    addCustomer: "Müşteri Ekle",
    editCustomer: "Müşteri Düzenle",
    companyName: "Firma Adı",
    address: "Adres",
    city: "Şehir",
    country: "Ülke",
    taxOffice: "Vergi Dairesi",
    taxNumber: "Vergi No",
    notes: "Notlar",
    contactPersons: "İletişim Kişileri",
    addContact: "Kişi Ekle",
    name: "Ad",
    title: "Ünvan",
    email: "E-posta",
    phone: "Telefon",
    primaryContact: "Ana İletişim",

    // Products
    products: "Ürünler",
    addProduct: "Ürün Ekle",
    editProduct: "Ürün Düzenle",
    brand: "Marka",
    model: "Model",
    models: "Modeller",
    category: "Kategori",
    itemName: "Ürün Adı",
    description: "Açıklama",
    defaultValues: "Varsayılan Değerler",
    unit: "Birim",
    currency: "Para Birimi",
    unitPrice: "Birim Fiyat",
    costPrice: "Maliyet Fiyatı",
    sku: "SKU",
    addModel: "Model Ekle",
    modelName: "Model Adı",

    // Quotations
    quotations: "Teklifler",
    newQuotation: "Yeni Teklif",
    quotationNo: "Teklif No",
    date: "Tarih",
    customer: "Müşteri",
    subject: "Konu",
    projectCode: "Proje Kodu",
    validity: "Geçerlilik",
    days: "gün",
    language: "Dil",
    turkish: "Türkçe",
    english: "İngilizce",

    salesQuotations: "Satış Teklifleri",
    serviceQuotations: "Hizmet Teklifleri",
    createManageProductSales: "Ürün satış teklifleri oluştur ve yönet",
    createManageService: "Hizmet teklifleri oluştur ve yönet",

    demartRepresentatives: "DEMART Yetkilileri",
    manageRepresentatives: "Yetkilileri yönet",

    costReports: "Maliyet Raporları",
    viewCostAnalysis: "Maliyet analizini görüntüle",

    // Status
    pending: "Beklemede", // (senin ekrandaki ile uyumlu olsun diye Beklemede yaptım)
    accepted: "Kabul Edilen",
    approved: "Onaylandı",
    rejected: "Reddedildi",

    representative: "Yetkili",
    deliveryTime: "Teslimat Süresi",
    deliveryTerms: "Teslimat Koşulları",
    paymentTerms: "Ödeme Koşulları",
    mainCurrency: "Para Birimi (Tüm Teklif İçin)",
    shippingTerm: "Nakliye Şartları",
    importExtraCost: "İthalat Ek Maliyeti",

    lineItems: "Kalemler",
    addItem: "Kalem Ekle",
    optional: "Opsiyonel",
    lineNote: "Satır Notu",

    createQuotation: "Teklif Oluştur",
    updatingQuotation: "Teklif güncelleniyor...",
    creatingQuotation: "Teklif oluşturuluyor...",

    selectCustomer: "Müşteri Seçin",
    selectRepresentative: "Yetkili Seçin",
    selectProduct: "Ürün Seçin",

    noCustomersFound: "Müşteri bulunamadı - önce müşteri ekleyin",
    noProductsFound: "Ürün bulunamadı - manuel giriş yapın",
    manualEntry: "Manuel Giriş",

    // Dashboard / Home (EKLENDİ)
    dashboard_warehouse: "Depo / Stok Yönetimi",
    dashboard_warehouse_desc: "Çoklu depo, raf adresleme ve stok takibi",
    dashboard_inventory: "Envanter Yönetimi",
    dashboard_inventory_desc: "Ofis, atölye, el aletleri ve araç envanteri",
    dashboard_service: "Servis Yönetimi",
    dashboard_service_desc: "Servis raporları ve müşteri takibi",

    dashboard_this_month: "Bu Ay Teklifler",
    dashboard_last_5: "Son 5 Teklif",
    dashboard_monthly_income_expense: "Aylık Gelir/Gider",
    dashboard_password_required: "Şifre gerekli",
    dashboard_show: "Göster",

    real_costs: "Gerçek Maliyetler",
    bank_expense_analysis: "Banka harcama analizi",

    // PDF Content
    customerInfo: "Müşteri Bilgileri",
    demartRepresentative: "DEMART Yetkilisi",
    quotationItems: "Teklif Kalemleri",
    optionalItems: "Opsiyonel Kalemler",
    quantity: "Miktar",
    total: "Toplam",
    subtotal: "Ara Toplam",
    discount: "İndirim",
    grandTotal: "Genel Toplam",
    confidentialityNotice: "GİZLİLİK UYARISI",
    validityNote: "Geçerlilik",
    pricesExcludeVAT: "Bu teklifte belirtilen tüm fiyatlar KDV ve diğer yasal vergiler hariçtir.",

    // Confirmation messages
    confirmDeleteUnsaved: "Kaydetmeden çıkmak üzeresiniz. Tüm değişiklikler kaybolacak. Emin misiniz?",

    // Toast messages - Customers
    customerUpdated: "Müşteri güncellendi",
    customerCreated: "Müşteri oluşturuldu",
    customerSaveFailed: "Müşteri kaydedilemedi",
    customerDeleted: "müşterisi silindi",
    customerDeleteFailed: "Müşteri silinemedi",

    // Toast messages - Products
    productUpdated: "Ürün güncellendi",
    productCreated: "Ürün oluşturuldu",
    productSaveFailed: "Ürün kaydedilemedi",
    productDeleted: "ürünü silindi",
    productDeleteFailed: "Ürün silinemedi",

    // Confirmation dialogs
    confirmDeleteCustomerWithQuotations:
      "DİKKAT!\n\nmüşterisinin adet teklifi var!\n\nBu müşteriyi silerseniz geçmiş tekliflerle ilişkisi kaybolur.\n\nSilmek istediğinize emin misiniz?",
    confirmDeleteCustomerFinal:
      "SON UYARI!\n\nBu işlem GERİ ALINAMAZ!\n\nmüşterisini kalıcı olarak silmek istediğinizden EMİN misiniz?\n\nTeklifler: adet",
    confirmDeleteCustomerSimple: "müşterisini silmek istediğinize emin misiniz?",
    confirmDeleteProductSimple: "ürününü silmek istediğinize emin misiniz?",

    // UI States
    loading: "Yükleniyor...",
    saving: "Kaydediliyor...",
    noCustomersYet: "Henüz müşteri yok",
    noProductsYet: "Henüz ürün yok",
    addContactPerson: "İrtibat kişisi ekleyin",
    manageCustomerDatabase: "Müşteri veritabanınızı yönetin",
    manageProductCatalog: "Ürün kataloğunuzu yönetin",
    contact: "Kişi",
    contacts: "Kişiler",
    andMore: "daha fazla",

    // Placeholders
    placeholderTitle: "örn., Satın Alma Müdürü",

    // Misc
    warning: "⚠️",
    attention: "DİKKAT!",
    finalWarning: "SON UYARI!",
    cannotBeUndone: "Bu işlem GERİ ALINAMAZ!"
  },

  en: {
    // Common
    save: "Save",
    cancel: "Cancel",
    edit: "Edit",
    delete: "Delete",
    add: "Add",

    // Customers
    customers: "Customers",
    addCustomer: "Add Customer",
    editCustomer: "Edit Customer",
    companyName: "Company Name",
    address: "Address",
    city: "City",
    country: "Country",
    taxOffice: "Tax Office",
    taxNumber: "Tax Number",
    notes: "Notes",
    contactPersons: "Contact Persons",
    addContact: "Add Contact",
    name: "Name",
    title: "Title",
    email: "Email",
    phone: "Phone",
    primaryContact: "Primary Contact",

    // Products
    products: "Products",
    addProduct: "Add Product",
    editProduct: "Edit Product",
    brand: "Brand",
    model: "Model",
    models: "Models",
    category: "Category",
    itemName: "Item Name",
    description: "Description",
    defaultValues: "Default Values",
    unit: "Unit",
    currency: "Currency",
    unitPrice: "Unit Price",
    costPrice: "Cost Price",
    sku: "SKU",
    addModel: "Add Model",
    modelName: "Model Name",

    // Quotations
    quotations: "Quotations",
    newQuotation: "New Quotation",
    quotationNo: "Quotation No",
    date: "Date",
    customer: "Customer",
    subject: "Subject",
    projectCode: "Project Code",
    validity: "Validity",
    days: "days",
    language: "Language",
    turkish: "Turkish",
    english: "English",

    salesQuotations: "Sales Quotations",
    serviceQuotations: "Service Quotations",
    createManageProductSales: "Create and manage product sales quotations",
    createManageService: "Create and manage service quotations",

    demartRepresentatives: "DEMART Representatives",
    manageRepresentatives: "Manage representatives",

    costReports: "Cost Reports",
    viewCostAnalysis: "View cost analysis",

    // Status
    pending: "Pending",
    accepted: "Accepted",
    approved: "Approved",
    rejected: "Rejected",

    representative: "Representative",
    deliveryTime: "Delivery Time",
    deliveryTerms: "Delivery Terms",
    paymentTerms: "Payment Terms",
    mainCurrency: "Currency (For Entire Quotation)",
    shippingTerm: "Shipping Terms",
    importExtraCost: "Import Extra Cost",

    lineItems: "Line Items",
    addItem: "Add Item",
    optional: "Optional",
    lineNote: "Line Note",

    createQuotation: "Create Quotation",
    updatingQuotation: "Updating quotation...",
    creatingQuotation: "Creating quotation...",

    selectCustomer: "Select Customer",
    selectRepresentative: "Select Representative",
    selectProduct: "Select Product",

    noCustomersFound: "No customers found - add customer first",
    noProductsFound: "No products found - enter manually",
    manualEntry: "Manual Entry",

    // Dashboard / Home (EKLENDİ)
    dashboard_warehouse: "Warehouse / Stock Management",
    dashboard_warehouse_desc: "Multi-warehouse, shelf addressing and stock tracking",
    dashboard_inventory: "Inventory Management",
    dashboard_inventory_desc: "Office, workshop, tools and vehicle inventory",
    dashboard_service: "Service Management",
    dashboard_service_desc: "Service reports and customer tracking",

    dashboard_this_month: "This Month Quotations",
    dashboard_last_5: "Last 5 Quotations",
    dashboard_monthly_income_expense: "Monthly Income / Expense",
    dashboard_password_required: "Password required",
    dashboard_show: "Show",

    real_costs: "Actual Costs",
    bank_expense_analysis: "Bank expense analysis",

    // PDF Content
    customerInfo: "Customer Information",
    demartRepresentative: "DEMART Representative",
    quotationItems: "Quotation Items",
    optionalItems: "Optional Items",
    quantity: "Quantity",
    total: "Total",
    subtotal: "Subtotal",
    discount: "Discount",
    grandTotal: "Grand Total",
    confidentialityNotice: "CONFIDENTIALITY NOTICE",
    validityNote: "Validity",
    pricesExcludeVAT: "All prices stated in this quotation exclude VAT and other legal taxes.",

    // Confirmation messages
    confirmDeleteUnsaved:
      "You are about to exit without saving. All changes will be lost. Are you sure?",

    // Toast messages - Customers
    customerUpdated: "Customer updated",
    customerCreated: "Customer created",
    customerSaveFailed: "Failed to save customer",
    customerDeleted: "customer deleted",
    customerDeleteFailed: "Failed to delete customer",

    // Toast messages - Products
    productUpdated: "Product updated",
    productCreated: "Product created",
    productSaveFailed: "Failed to save product",
    productDeleted: "product deleted",
    productDeleteFailed: "Failed to delete product",

    // Confirmation dialogs
    confirmDeleteCustomerWithQuotations:
      "ATTENTION!\n\ncustomer has quotations!\n\nIf you delete this customer, the relationship with past quotations will be lost.\n\nAre you sure you want to delete?",
    confirmDeleteCustomerFinal:
      "FINAL WARNING!\n\nThis action CANNOT BE UNDONE!\n\nAre you SURE you want to permanently delete customer?\n\nQuotations: count",
    confirmDeleteCustomerSimple: "Are you sure you want to delete customer?",
    confirmDeleteProductSimple: "Are you sure you want to delete product?",

    // UI States
    loading: "Loading...",
    saving: "Saving...",
    noCustomersYet: "No customers yet",
    noProductsYet: "No products yet",
    addContactPerson: "Add contact person",
    manageCustomerDatabase: "Manage your customer database",
    manageProductCatalog: "Manage your product catalog",
    contact: "Contact",
    contacts: "Contacts",
    andMore: "more",

    // Placeholders
    placeholderTitle: "e.g., Purchasing Manager",

    // Misc
    warning: "⚠️",
    attention: "ATTENTION!",
    finalWarning: "FINAL WARNING!",
    cannotBeUndone: "This action CANNOT BE UNDONE!"
  }
};

// BASİT KULLANIM FONKSİYONU
export const t = (key, lang = "tr") => {
  return translations[lang]?.[key] || key;
};

export const useTranslation = () => {
  // Global language state - şimdilik localStorage'dan alıyoruz
  const getCurrentLanguage = () => {
    return localStorage.getItem("appLanguage") || "tr";
  };

  const setLanguage = (lang) => {
    localStorage.setItem("appLanguage", lang);
    window.location.reload(); // Basit yöntem - sayfa yenilenir
  };

  const t = (key) => {
    const lang = getCurrentLanguage();
    return translations[lang]?.[key] || key;
  };

  return { t, currentLanguage: getCurrentLanguage(), setLanguage };
};
