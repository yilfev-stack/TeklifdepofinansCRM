import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { toast } from 'sonner';
import QuotationFiles from '@/components/QuotationFiles';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QuotationPreview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quotation, setQuotation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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

    fetchQuotation();
  }, [id]);

  const handleDownloadPDF = async () => {
    const toastId = toast.loading('PDF hazırlanıyor...');
    const primaryUrl = `${API}/quotations/${id}/generate-pdf-native`;
    const fallbackUrl = `${API}/quotations/${id}/generate-pdf-v2`;
    const secondFallbackUrl = `${API}/quotations/${id}/generate-pdf`;

    try {
      const response = await fetch(primaryUrl, { method: 'HEAD' });
      const targetUrl = response.ok ? primaryUrl : fallbackUrl;
      window.location.assign(targetUrl);
      toast.success('PDF indiriliyor...', { id: toastId });
    } catch (error) {
      console.error('PDF export error:', error);
      window.location.assign(secondFallbackUrl);
      toast.success('PDF indiriliyor...', { id: toastId });
    }
  };

  if (loading) {
    return <div className="p-6">Yükleniyor...</div>;
  }

  if (!quotation) {
    return <div className="p-6">Teklif bulunamadı.</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Button variant="outline" onClick={() => navigate(-1)}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Geri Dön
        </Button>
        <Button onClick={handleDownloadPDF}>
          <Download className="mr-2 h-4 w-4" />
          PDF İndir
        </Button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-gray-900">{quotation.proje_basligi}</h1>
          <p className="text-sm text-gray-600">
            {quotation.musteri_firma_adi} • {quotation.teklif_no}
          </p>
          <p className="text-sm text-gray-600">
            {quotation.representative_name} • {quotation.representative_email}
          </p>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <QuotationFiles quotationId={id} />
      </div>
    </div>
  );
};

export default QuotationPreview;
