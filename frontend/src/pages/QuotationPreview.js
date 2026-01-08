import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  ArrowLeft,
  Download,
  Edit,
  FileText,
  Lock,
  Plus,
  Trash2,
  GitBranch,
  History,
  Upload,
  CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';
import ProposalCover from '@/components/ProposalCover';
import QuotationFiles from '@/components/QuotationFiles';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QuotationPreview = () => {
  const { type, id } = useParams();
  const navigate = useNavigate();

  const [quotation, setQuotation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('preview');
  const [costsDialogOpen, setCostsDialogOpen] = useState(false);
  const [internalCosts, setInternalCosts] = useState([]);
  const [costCategories, setCostCategories] = useState([]);
  const [costForm, setCostForm] = useState({
    category_id: '',
    description: '',
    amount: 0,
    currency: 'EUR'
  });
  const [revisionDialogOpen, setRevisionDialogOpen] = useState(false);
  const [revisions, setRevisions] = useState([]);
  const [loadingRevisions, setLoadingRevisions] = useState(false);
  const [uploadingPdf, setUploadingPdf] = useState(false);
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    fetchQuotation();
    fetchCostCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchQuotation = async () => {
    try {
      const response = await axios.get(`${API}/quotations/${id}`);
      setQuotation(response.data);
    } catch (error) {
      console.error('Error fetching quotation:', error);
      toast.error('Teklif yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    const toastId = toast.loading('PDF hazırlanıyor...');
    const primaryUrl = `${API}/quotations/${id}/generate-pdf-v2`;
    const fallbackUrl = `${API}/quotations/${id}/generate-pdf`;

    try {
      const response = await fetch(primaryUrl, { method: 'HEAD' });
      const targetUrl = response.ok ? primaryUrl : fallbackUrl;
      window.location.assign(targetUrl);
      toast.success('PDF indiriliyor...', { id: toastId });
    } catch (error) {
      console.error('PDF export error:', error);
      window.location.assign(fallbackUrl);
      toast.success('PDF indiriliyor...', { id: toastId });

    try {
      let response;
      try {
        response = await axios.get(`${API}/quotations/${id}/generate-pdf-v2`, {
          responseType: 'blob'
        });
      } catch (error) {
        response = await axios.get(`${API}/quotations/${id}/generate-pdf`, {
          responseType: 'blob'
        });
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `Teklif-${quotation.quote_no}-${quotation.customer_name}.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('PDF başarıyla indirildi!', { id: toastId });
    } catch (error) {
      console.error('PDF export error:', error);
      toast.error('PDF indirilemedi', { id: toastId });
    }
  };

  // Upload edited PDF
  const handleUploadEditedPdf = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Sadece PDF dosyası yüklenebilir');
      return;
    }

    setUploadingPdf(true);
    const toastId = toast.loading('PDF yükleniyor...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      await axios.post(`${API}/quotations/${id}/upload-edited-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast.success('Düzenlenmiş PDF başarıyla yüklendi!', { id: toastId });
      fetchQuotation(); // Refresh to get updated has_edited_pdf status
    } catch (error) {
      console.error('PDF upload error:', error);
      toast.error(error.response?.data?.detail || 'PDF yüklenemedi', { id: toastId });
    } finally {
      setUploadingPdf(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Download edited PDF
  const handleDownloadEditedPdf = async () => {
    try {
      const response = await axios.get(`${API}/quotations/${id}/download-edited-pdf`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Teklif-${quotation.quote_no}-DUZENLENMIS.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Düzenlenmiş PDF indirildi!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('PDF indirilemedi');
    }
  };

  const fetchInternalCosts = async () => {
    try {
      const response = await axios.get(`${API}/quotations/${id}/internal-costs`);
      setInternalCosts(response.data);
    } catch (error) {
      console.error('Error fetching internal costs:', error);
    }
  };

  const fetchCostCategories = async () => {
    try {
      const response = await axios.get(`${API}/cost-categories`);
      setCostCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleAddInternalCost = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/internal-costs`, {
        quotation_id: id,
        ...costForm
      });
      toast.success('Internal cost added');
      setCostForm({ category_id: '', description: '', amount: 0, currency: 'EUR' });
      fetchInternalCosts();
    } catch (error) {
      console.error('Error adding cost:', error);
      toast.error('Failed to add cost');
    }
  };

  const handleDeleteCost = async (costId) => {
    try {
      await axios.delete(`${API}/internal-costs/${costId}`);
      toast.success('Cost deleted');
      fetchInternalCosts();
    } catch (error) {
      console.error('Error deleting cost:', error);
      toast.error('Failed to delete cost');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount, currency) => {
    return `${amount.toFixed(2)} ${currency}`;
  };

  const calculateInternalCostsTotals = () => {
    const totals = {};
    internalCosts.forEach((cost) => {
      totals[cost.currency] = (totals[cost.currency] || 0) + cost.amount;
    });
    return totals;
  };

  const calculateProfit = () => {
    if (!quotation) return null;
    const customerTotals = quotation.totals_by_currency?.totals || {};
    const costTotals = calculateInternalCostsTotals();

    const profits = {};
    Object.keys(customerTotals).forEach((currency) => {
      const revenue = customerTotals[currency] || 0;
      const cost = costTotals[currency] || 0;
      profits[currency] = revenue - cost;
    });

    return profits;
  };

  const handleNewRevision = async () => {
    try {
      const response = await axios.post(`${API}/quotations/${id}/revise`);
      toast.success('Yeni revizyon oluşturuldu!');
      navigate(`/quotations/${type}/edit/${response.data.id}`);
    } catch (error) {
      console.error('Revision error:', error);
      toast.error('Revizyon oluşturulamadı');
    }
  };

  const handleViewRevisions = async () => {
    setLoadingRevisions(true);
    setRevisionDialogOpen(true);
    try {
      const response = await axios.get(`${API}/quotations/${id}/revisions`);
      setRevisions(response.data);
    } catch (error) {
      console.error('Error fetching revisions:', error);
      toast.error('Revizyonlar yüklenemedi');
      setRevisions([]);
    } finally {
      setLoadingRevisions(false);
    }
  };

  if (loading || !quotation) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  const proposalData = {
    teklif_no: quotation.quote_no,
    tarih: quotation.date,
    musteri_firma_adi: quotation.customer_name,
    proje_basligi: quotation.subject,
    representative_name: quotation.representative_name,
    representative_phone: quotation.representative_phone,
    representative_email: quotation.representative_email,
    language: quotation.language
  };

  return (
    <div className="min-h-screen bg-background">
      {/* TOP BAR */}
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-10 print:hidden">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(`/quotations/${type}`)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-heading font-bold">Quotation Preview</h1>
                <p className="text-xs text-muted-foreground">{quotation.quote_no}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant={activeTab === 'preview' ? 'default' : 'outline'}
                onClick={() => setActiveTab('preview')}
              >
                Önizleme
              </Button>
              <Button
                variant={activeTab === 'files' ? 'default' : 'outline'}
                onClick={() => setActiveTab('files')}
              >
                <FileText className="h-4 w-4 mr-2" />
                Dosyalar
              </Button>
              <Button
                variant="outline"
                onClick={handleNewRevision}
                className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
              >
                <GitBranch className="h-4 w-4 mr-2" />
                Yeni Revizyon
              </Button>
              <Button
                variant="outline"
                onClick={handleViewRevisions}
                className="border-blue-500/50 text-blue-400 hover:bg-blue-500/10"
              >
                <History className="h-4 w-4 mr-2" />
                Revizyon Geçmişi
              </Button>

              {/* INTERNAL COSTS DIALOG */}
              <Dialog
                open={costsDialogOpen}
                onOpenChange={(open) => {
                  setCostsDialogOpen(open);
                  if (open) fetchInternalCosts();
                }}
              >
                <DialogTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                  >
                    <Lock className="h-4 w-4 mr-2" />
                    Internal Costs (SECRET)
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle className="text-red-400">
                      🔒 Internal Real Costs (Private)
                    </DialogTitle>
                  </DialogHeader>

                  <div className="space-y-6 mt-4">
                    <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded">
                      <div className="text-sm font-semibold text-blue-400 mb-2">
                        Customer Grand Total (Reference):
                      </div>
                      {Object.keys(quotation.totals_by_currency?.totals || {}).map(
                        (currency) => (
                          <div key={currency} className="text-xl font-bold">
                            {formatCurrency(
                              quotation.totals_by_currency.totals[currency],
                              currency
                            )}
                          </div>
                        )
                      )}
                    </div>

                    <details className="p-3 bg-muted/10 rounded border border-muted">
                      <summary className="cursor-pointer text-sm font-semibold">
                        + New Cost Category
                      </summary>
                      <div className="mt-3 space-y-2">
                        <Input
                          placeholder="Category name (e.g., Flight Tickets)"
                          id="new-category-name"
                        />
                        <Button
                          size="sm"
                          onClick={async () => {
                            const nameInput = document.getElementById(
                              'new-category-name'
                            );
                            if (!nameInput || !nameInput.value) {
                              toast.error('Enter category name');
                              return;
                            }
                            try {
                              await axios.post(`${API}/cost-categories`, {
                                name: nameInput.value,
                                scope: 'both'
                              });
                              toast.success('Category added');
                              nameInput.value = '';
                              fetchCostCategories();
                            } catch (error) {
                              toast.error('Failed to add category');
                            }
                          }}
                        >
                          Add Category
                        </Button>
                      </div>
                    </details>

                    <form
                      onSubmit={handleAddInternalCost}
                      className="p-4 bg-muted/20 rounded space-y-3"
                    >
                      <h3 className="font-semibold">Add Internal Cost</h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>Category</Label>
                          <select
                            className="w-full p-2 border rounded bg-background"
                            value={costForm.category_id}
                            onChange={(e) =>
                              setCostForm({ ...costForm, category_id: e.target.value })
                            }
                            required
                          >
                            <option value="">Select...</option>
                            {costCategories.map((cat) => (
                              <option key={cat.id} value={cat.id}>
                                {cat.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <Label>Amount</Label>
                          <Input
                            type="number"
                            step="0.01"
                            value={costForm.amount}
                            onChange={(e) =>
                              setCostForm({
                                ...costForm,
                                amount: parseFloat(e.target.value || '0')
                              })
                            }
                            required
                          />
                        </div>
                        <div>
                          <Label>Currency</Label>
                          <select
                            className="w-full p-2 border rounded bg-background"
                            value={costForm.currency}
                            onChange={(e) =>
                              setCostForm({ ...costForm, currency: e.target.value })
                            }
                          >
                            <option value="EUR">EUR</option>
                            <option value="USD">USD</option>
                            <option value="TRY">TRY</option>
                          </select>
                        </div>
                        <div>
                          <Label>Description</Label>
                          <Input
                            value={costForm.description}
                            onChange={(e) =>
                              setCostForm({ ...costForm, description: e.target.value })
                            }
                            required
                          />
                        </div>
                      </div>
                      <Button type="submit" size="sm">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Cost
                      </Button>
                    </form>

                    <div className="space-y-2">
                      <h3 className="font-semibold">Internal Costs:</h3>
                      {internalCosts.length === 0 ? (
                        <p className="text-sm text-muted-foreground">
                          No internal costs added yet
                        </p>
                      ) : (
                        internalCosts.map((cost) => (
                          <div
                            key={cost.id}
                            className="p-3 bg-background border rounded flex justify-between items-center"
                          >
                            <div>
                              <div className="font-semibold">{cost.category_name}</div>
                              <div className="text-sm text-muted-foreground">
                                {cost.description}
                              </div>
                              <div className="text-accent font-mono">
                                {formatCurrency(cost.amount, cost.currency)}
                              </div>
                            </div>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteCost(cost.id)}
                              className="hover:bg-destructive/10 hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))
                      )}
                    </div>

                    {internalCosts.length > 0 && (
                      <div className="space-y-3 pt-4 border-t">
                        <div>
                          <div className="text-sm font-semibold text-muted-foreground mb-2">
                            Total Internal Costs:
                          </div>
                          {Object.keys(calculateInternalCostsTotals()).map(
                            (currency) => (
                              <div
                                key={currency}
                                className="text-lg font-bold text-red-400"
                              >
                                {formatCurrency(
                                  calculateInternalCostsTotals()[currency],
                                  currency
                                )}
                              </div>
                            )
                          )}
                        </div>

                        <div className="p-4 bg-green-500/10 border border-green-500/30 rounded">
                          <div className="text-sm font-semibold text-green-400 mb-2">
                            Profit:
                          </div>
                          {Object.keys(calculateProfit() || {}).map((currency) => (
                            <div
                              key={currency}
                              className="text-xl font-bold text-green-400"
                            >
                              {formatCurrency(
                                (calculateProfit() || {})[currency],
                                currency
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </DialogContent>
              </Dialog>

              <Button variant="outline" onClick={() => navigate(`/quotations/${type}/edit/${id}`)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button onClick={handleDownloadPDF}>
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>

              {/* Edited PDF Section */}
              <div className="border-l pl-4 ml-2 flex items-center gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".pdf"
                  onChange={handleUploadEditedPdf}
                  className="hidden"
                />
                <Button 
                  variant="outline" 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingPdf}
                  className="border-orange-500 text-orange-600 hover:bg-orange-50"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {uploadingPdf ? 'Yükleniyor...' : 'Düzenlenmiş PDF Yükle'}
                </Button>

                {quotation?.has_edited_pdf && (
                  <Button 
                    onClick={handleDownloadEditedPdf}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Düzenlenmiş PDF İndir
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* REVISION HISTORY DIALOG */}
      <Dialog open={revisionDialogOpen} onOpenChange={setRevisionDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>📜 Revizyon Geçmişi</DialogTitle>
          </DialogHeader>
          {loadingRevisions ? (
            <div className="text-center py-8">Yükleniyor...</div>
          ) : revisions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Henüz revizyon yok
            </div>
          ) : (
            <div className="space-y-2">
              {revisions.map((rev) => (
                <div
                  key={rev.id}
                  className="p-4 border rounded hover:bg-accent/5 cursor-pointer"
                  onClick={() => navigate(`/quotations/${type}/preview/${rev.id}`)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{rev.quote_no}</div>
                      <div className="text-sm text-muted-foreground">
                        {formatDate(rev.date)} | {rev.offer_status}
                      </div>
                    </div>
                    {rev.id === quotation.id && (
                      <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                        Current
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* MAIN CONTENT */}
      <div className="container mx-auto px-6 py-8 max-w-5xl">
        {activeTab === 'preview' ? (
          <div className="space-y-8">
            {/* COVER PAGE */}
            <div className="aspect-[210/297] w-full shadow-2xl">
              <ProposalCover proposal={proposalData} />
            </div>

            {/* PAGE 2 - MAIN OFFER */}
            <div className="relative bg-white text-gray-900 p-12 rounded shadow-2xl print-content">
              {/* Header */}
              <div className="pb-6 mb-6 border-b border-gray-200 relative z-30">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-gray-700">
                      {quotation.language === 'english' ? 'Quotation No:' : 'Teklif No:'}{' '}
                      {quotation.quote_no}
                    </p>
                    <p className="text-sm text-gray-700">
                      {quotation.language === 'english' ? 'Date:' : 'Tarih:'}{' '}
                      {formatDate(quotation.date)}
                    </p>
                  </div>
                  <div className="text-right">
                    <img
                      src="/images/demart-logo.jpg"
                      alt="DEMART Logo"
                      className="h-16 w-auto mb-1 ml-auto"
                    />
                    <div
                      className="text-[10px] font-medium uppercase tracking-wide"
                      style={{ color: '#004aad' }}
                    >
                      The Art of Design Engineering Maintenance
                    </div>
                  </div>
                </div>
              </div>

              {/* Watermark */}
              <div
                className="absolute inset-0 flex items-center justify-center pointer-events-none z-5"
                style={{
                  transform: 'rotate(-45deg)',
                  opacity: 0.05
                }}
              >
                <div className="text-[140px] font-black tracking-widest text-gray-300">
                  DEMART
                </div>
              </div>

              <div className="relative space-y-8 z-20">
                {/* Customer / Demart blocks */}
                <div className="grid grid-cols-2 gap-6">
                  <div className="border border-gray-300 p-4 bg-gray-50">
                    <div
                      style={{
                        borderLeft: '5px solid #dc2626',
                        paddingLeft: '12px',
                        marginBottom: '12px',
                        backgroundColor: 'transparent'
                      }}
                    >
                      <h3 className="text-base font-bold text-gray-900">
                        {quotation.language === 'english'
                          ? 'Customer Information'
                          : 'Müşteri Bilgileri'}
                      </h3>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">
                          {quotation.language === 'english' ? 'Company:' : 'Firma:'}
                        </span>{' '}
                        <span className="text-gray-900 font-semibold">
                          {quotation.customer_name}
                        </span>
                      </div>
                      {quotation.customer_details && (
                        <>
                          {quotation.customer_details.contact_person && (
                            <div>
                              <span className="font-medium text-gray-700">
                                {quotation.language === 'english' ? 'Contact:' : 'Yetkili:'}
                              </span>{' '}
                              <span className="text-gray-900">
                                {quotation.customer_details.contact_person}
                              </span>
                            </div>
                          )}
                          {quotation.customer_details.phone && (
                            <div>
                              <span className="font-medium text-gray-700">
                                {quotation.language === 'english' ? 'Phone:' : 'Telefon:'}
                              </span>{' '}
                              <span className="text-gray-900">
                                {quotation.customer_details.phone}
                              </span>
                            </div>
                          )}
                          {quotation.customer_details.email && (
                            <div>
                              <span className="font-medium text-gray-700">
                                {quotation.language === 'english' ? 'Email:' : 'E-posta:'}
                              </span>{' '}
                              <span className="text-gray-900">
                                {quotation.customer_details.email}
                              </span>
                            </div>
                          )}
                          {(quotation.customer_details.address ||
                            quotation.customer_details.city ||
                            quotation.customer_details.country) && (
                            <div>
                              <span className="font-medium text-gray-700">
                                {quotation.language === 'english' ? 'Address:' : 'Adres:'}
                              </span>{' '}
                              <span className="text-gray-900">
                                {quotation.customer_details.address}
                                {quotation.customer_details.city &&
                                  `, ${quotation.customer_details.city}`}
                                {quotation.customer_details.country &&
                                  `, ${quotation.customer_details.country}`}
                              </span>
                            </div>
                          )}
                        </>
                      )}
                      {quotation.project_code && (
                        <div>
                          <span className="font-medium text-gray-700">
                            {quotation.language === 'english'
                              ? 'Request No:'
                              : 'Talep No:'}
                          </span>{' '}
                          <span className="text-gray-900">{quotation.project_code}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {quotation.representative_name && (
                    <div className="border border-gray-300 p-4 bg-gray-50">
                      <div
                        style={{
                          borderLeft: '5px solid #dc2626',
                          paddingLeft: '12px',
                          marginBottom: '12px',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <h3 className="text-base font-bold text-gray-900">
                          {quotation.language === 'english'
                            ? 'DEMART Representative'
                            : 'DEMART Yetkilisi'}
                        </h3>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">
                            {quotation.language === 'english' ? 'Name:' : 'Ad Soyad:'}
                          </span>{' '}
                          <span className="font-semibold" style={{ color: '#004aad' }}>
                            {quotation.representative_name}
                          </span>
                        </div>
                        {quotation.representative_phone && (
                          <div>
                            <span className="font-medium text-gray-700">
                              {quotation.language === 'english' ? 'Phone:' : 'Telefon:'}
                            </span>{' '}
                            <span style={{ color: '#004aad' }}>
                              {quotation.representative_phone}
                            </span>
                          </div>
                        )}
                        {quotation.representative_email && (
                          <div>
                            <span className="font-medium text-gray-700">
                              {quotation.language === 'english' ? 'Email:' : 'E-posta:'}
                            </span>{' '}
                            <span style={{ color: '#004aad' }}>
                              {quotation.representative_email}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Greeting / intro */}
                {quotation.customer_details && (
                  <div
                    className="border-l-4 pl-4 py-3 my-4"
                    style={{ borderColor: '#dc2626', backgroundColor: '#fef2f2' }}
                  >
                    <p className="text-sm text-gray-800 mb-2">
                      {quotation.customer_details.contact_person
                        ? quotation.language === 'english'
                          ? `Dear ${quotation.customer_details.contact_person},`
                          : `Sayın ${quotation.customer_details.contact_person},`
                        : quotation.language === 'english'
                        ? 'Dear Sir/Madam,'
                        : 'Sayın Yetkili,'}
                    </p>
                    <p className="text-sm text-gray-700">
                      {quotation.language === 'english'
                        ? 'The quotation document prepared upon your request is hereby submitted for your review.'
                        : 'Talebinize istinaden hazırlanan teklif dokümanı değerlendirilmek üzere bilginize sunulmuştur.'}
                    </p>
                  </div>
                )}

                {/* Line items table */}
                <div>
                  <div
                    style={{
                      borderLeft: '5px solid #dc2626',
                      paddingLeft: '12px',
                      marginBottom: '12px',
                      backgroundColor: 'transparent'
                    }}
                  >
                    <h3 className="text-base font-bold text-gray-900">
                      {quotation.language === 'english'
                        ? 'Products / Services'
                        : 'Ürünler / Hizmetler'}
                    </h3>
                  </div>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-400">
                        <th className="text-center py-2 font-semibold w-12">#</th>
                        <th className="text-left py-2 font-semibold">
                          {quotation.language === 'english' ? 'Description' : 'Açıklama'}
                        </th>
                        <th className="text-center py-2 font-semibold">
                          {quotation.language === 'english' ? 'Quantity' : 'Miktar'}
                        </th>
                        <th className="text-center py-2 font-semibold">
                          {quotation.language === 'english' ? 'Unit' : 'Birim'}
                        </th>
                        <th className="text-right py-2 font-semibold">
                          {quotation.language === 'english'
                            ? 'Unit Price'
                            : 'Birim Fiyat'}
                        </th>
                        <th className="text-right py-2 font-semibold">
                          {quotation.language === 'english' ? 'Total' : 'Toplam'}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {quotation.line_items
                        .filter((item) => !item.is_optional)
                        .map((item, index) => (
                          <tr key={index} className="border-b border-gray-200 align-top">
                            <td className="py-3 text-center font-semibold text-gray-600">
                              {index + 1}
                            </td>
                            <td className="py-3">
                              <div className="font-semibold">{item.item_short_name}</div>
                              {item.variant_sku && (
                                <div className="text-xs text-gray-500 font-mono">
                                  SKU: {item.variant_sku}
                                </div>
                              )}
                              {item.item_description && (
                                <div className="text-xs text-gray-600">
                                  {item.item_description}
                                </div>
                              )}
                            </td>
                            <td className="py-3 text-center">{item.quantity}</td>
                            <td className="py-3 text-center">{item.unit}</td>
                            <td className="py-3 text-right">
                              {formatCurrency(item.unit_price, item.currency)}
                            </td>
                            <td className="py-3 text-right font-semibold">
                              {formatCurrency(item.line_total, item.currency)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>

                {/* Optional items */}
                {quotation.line_items.filter((item) => item.is_optional).length > 0 && (
                  <div>
                    <div
                      style={{
                        borderLeft: '5px solid #2563eb',
                        paddingLeft: '12px',
                        marginBottom: '12px',
                        backgroundColor: 'transparent'
                      }}
                    >
                      <h3 className="text-base font-bold text-gray-900">
                        {quotation.language === 'english'
                          ? 'Optional Items'
                          : 'Opsiyonel Kalemler'}
                      </h3>
                    </div>
                    <div className="space-y-2">
                      {quotation.line_items
                        .filter((item) => item.is_optional)
                        .map((item, index) => (
                          <div
                            key={index}
                            className="flex justify-between py-2 border-b border-gray-200"
                          >
                            <span className="text-sm">
                              {item.item_short_name}
                              {item.variant_sku && <span className="text-xs text-gray-500 ml-2">(SKU: {item.variant_sku})</span>}
                            </span>
                            <span className="text-sm font-semibold">
                              {formatCurrency(item.line_total, item.currency)}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Totals */}
                <div className="border-t-2 border-gray-300 pt-4 space-y-2">
                  {Object.keys(quotation.totals_by_currency?.totals || {}).map(
                    (currency) => {
                      const subtotal = quotation.line_items
                        .filter(
                          (item) => !item.is_optional && item.currency === currency
                        )
                        .reduce((sum, item) => sum + item.line_total, 0);

                      let discountAmount = 0;
                      if (
                        quotation.discount_type &&
                        quotation.discount_type !== 'none' &&
                        quotation.discount_value > 0 &&
                        quotation.discount_currency === currency
                      ) {
                        if (quotation.discount_type === 'percent') {
                          discountAmount = subtotal * (quotation.discount_value / 100);
                        } else {
                          discountAmount = quotation.discount_value;
                        }
                      }

                      const finalTotal = subtotal - discountAmount;

                      return (
                        <div key={currency}>
                          <div className="flex justify-between items-center py-1">
                            <span
                              className="font-semibold text-gray-700"
                              style={{ fontSize: '14px' }}
                            >
                              {quotation.language === 'english'
                                ? 'SUBTOTAL'
                                : 'ARA TOPLAM'}{' '}
                              ({currency}):
                            </span>
                            <span
                              className="font-bold text-gray-900"
                              style={{ fontSize: '14px' }}
                            >
                              {formatCurrency(subtotal, currency)}
                            </span>
                          </div>

                          {discountAmount > 0 && (
                            <div className="flex justify-between items-center py-1">
                              <span
                                className="font-semibold text-gray-700"
                                style={{ fontSize: '14px' }}
                              >
                                {quotation.language === 'english'
                                  ? 'DISCOUNT'
                                  : 'İNDİRİM'}
                                {quotation.discount_type === 'percent' &&
                                  ` (%${quotation.discount_value})`}
                                :
                              </span>
                              <span
                                className="font-bold text-red-600"
                                style={{ fontSize: '14px' }}
                              >
                                -{formatCurrency(discountAmount, currency)}
                              </span>
                            </div>
                          )}

                          <div className="flex justify-between items-center py-2 border-t-2 border-gray-400 mt-2">
                            <span
                              className="font-bold text-gray-900"
                              style={{ fontSize: '16px' }}
                            >
                              {quotation.language === 'english'
                                ? 'GRAND TOTAL'
                                : 'GENEL TOPLAM'}{' '}
                              ({currency}):
                            </span>
                            <span
                              className="font-bold"
                              style={{ color: '#004aad', fontSize: '18px' }}
                            >
                              {formatCurrency(finalTotal, currency)}
                            </span>
                          </div>
                        </div>
                      );
                    }
                  )}
                </div>

                {/* Notes / disclaimer */}
                <div
                  className="space-y-3 text-xs text-gray-600 border-t border-gray-200 pt-4"
                  style={{ pageBreakInside: 'avoid' }}
                >
                  <p className="italic">
                    {quotation.language === 'english'
                      ? 'All prices mentioned in this quotation are exclusive of VAT and other legal taxes.'
                      : 'Bu teklifte belirtilen tüm fiyatlar KDV ve diğer yasal vergiler hariçtir.'}
                  </p>
                  <p>
                    <span className="font-semibold">
                      {quotation.language === 'english' ? 'Validity:' : 'Geçerlilik:'}
                    </span>{' '}
                    {quotation.validity_days}{' '}
                    {quotation.language === 'english' ? 'days' : 'gün'}
                  </p>

                  <div className="bg-red-50 border border-red-200 p-4 rounded">
                    <h4 className="font-bold text-red-800 mb-2 text-sm">
                      {quotation.language === 'english'
                        ? 'CONFIDENTIALITY WARNING'
                        : 'GİZLİLİK UYARISI'}
                    </h4>
                    <p className="text-xs text-gray-700 leading-relaxed">
                      {quotation.language === 'english'
                        ? "This quotation has been prepared exclusively for the concerned company; all information, pricing, technical details, and documents contained herein are the property of DEMART MÜHENDİSLİK SAN. TİC. LTD. ŞTİ. and are protected under confidentiality principles and applicable legislation. Sharing, reproducing, or distributing it in any way to third parties without the written permission of DEMART is prohibited."
                        : "Bu teklif, yalnızca ilgili firmaya özel olarak hazırlanmış olup; içeriğindeki tüm bilgi, fiyatlandırma, teknik detaylar ve dokümanlar DEMART MÜHENDİSLİK SAN. TİC. LTD. ŞTİ.'nin mülkiyeti altında olup, gizlilik esasları ve yürürlükteki mevzuat kapsamında korunmaktadır. DEMART'ın yazılı izni olmaksızın üçüncü şahıslarla paylaşılması, çoğaltılması veya herhangi bir şekilde dağıtılması yasaktır."}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* PAGE 3 - TERMS */}
            <div
              className="relative bg-white text-gray-900 p-12 rounded shadow-2xl print-content"
              style={{ pageBreakBefore: 'always', paddingTop: 0 }}
            >
              <div className="pb-6 mb-6 border-b border-gray-200">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-gray-700">
                      {quotation.language === 'english' ? 'Quotation No:' : 'Teklif No:'}{' '}
                      {quotation.quote_no}
                    </p>
                    <p className="text-sm text-gray-700">
                      {quotation.language === 'english' ? 'Date:' : 'Tarih:'}{' '}
                      {formatDate(quotation.date)}
                    </p>
                  </div>
                  <div className="text-right">
                    <img
                      src="/images/demart-logo.jpg"
                      alt="DEMART Logo"
                      className="h-18 w-auto mb-1 ml-auto"
                    />
                    <div
                      className="text-[10px] font-medium uppercase tracking-wide"
                      style={{ color: '#004aad' }}
                    >
                      The Art of Design Engineering Maintenance
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4 text-sm">
                {quotation.delivery_time && (
                  <div>
                    <div
                      style={{
                        borderLeft: '5px solid #dc2626',
                        paddingLeft: '12px',
                        marginBottom: '8px'
                      }}
                    >
                      <h4 className="font-semibold" style={{ color: '#991b1b' }}>
                        {quotation.language === 'english'
                          ? 'Delivery Time:'
                          : 'Teslimat Süresi:'}
                      </h4>
                    </div>
                    <p className="text-gray-700">{quotation.delivery_time}</p>
                  </div>
                )}

                {quotation.delivery_terms && (
                  <div>
                    <div
                      style={{
                        borderLeft: '5px solid #dc2626',
                        paddingLeft: '12px',
                        marginBottom: '8px'
                      }}
                    >
                      <h4 className="font-semibold" style={{ color: '#991b1b' }}>
                        {quotation.language === 'english'
                          ? 'Delivery Terms:'
                          : 'Teslimat Koşulları:'}
                      </h4>
                    </div>
                    <p className="text-gray-700">{quotation.delivery_terms}</p>
                  </div>
                )}

                {quotation.payment_terms && (
                  <div>
                    <div
                      style={{
                        borderLeft: '5px solid #dc2626',
                        paddingLeft: '12px',
                        marginBottom: '8px'
                      }}
                    >
                      <h4 className="font-semibold" style={{ color: '#991b1b' }}>
                        {quotation.language === 'english'
                          ? 'Payment Terms:'
                          : 'Ödeme Koşulları:'}
                      </h4>
                    </div>
                    <p className="text-gray-700">{quotation.payment_terms}</p>
                  </div>
                )}

                {quotation.notes && (
                  <div>
                    <div
                      style={{
                        borderLeft: '5px solid #dc2626',
                        paddingLeft: '12px',
                        marginBottom: '8px'
                      }}
                    >
                      <h4 className="font-semibold" style={{ color: '#991b1b' }}>
                        {quotation.language === 'english' ? 'Notes:' : 'Notlar:'}
                      </h4>
                    </div>
                    <p className="text-gray-700">{quotation.notes}</p>
                  </div>
                )}
              </div>

              <div className="border-t border-gray-300 pt-4 mt-8 text-center">
                <p
                  className="text-xs font-medium uppercase tracking-wide"
                  style={{ color: '#004aad' }}
                >
                  THE ART OF DESIGN ENGINEERING MAINTENANCE
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-card p-6 rounded-lg shadow-lg">
            <QuotationFiles quotationId={id} />
          </div>
        )}
      </div>
    </div>
  );
};

export default QuotationPreview;
