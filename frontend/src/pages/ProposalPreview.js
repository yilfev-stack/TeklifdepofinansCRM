import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Edit } from "lucide-react";
import { toast } from "sonner";
import ProposalCover from "@/components/ProposalCover";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProposalPreview = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [proposal, setProposal] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProposal();
  }, [id]);

  const fetchProposal = async () => {
    try {
      const response = await axios.get(`${API}/proposals/${id}`);
      setProposal(response.data);
    } catch (error) {
      console.error("Teklif yüklenirken hata:", error);
      toast.error("Teklif yüklenemedi");
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => navigate('/')}
                className="hover:bg-primary/10 hover:text-primary"
                data-testid="back-btn"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-heading font-bold tracking-tight text-foreground">
                  Teklif Önizleme
                </h1>
                <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
                  {proposal?.teklif_no}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => navigate(`/edit/${id}`)}
                variant="outline"
                className="border-primary/50 hover:bg-primary/10 hover:text-primary"
                data-testid="edit-btn"
              >
                <Edit className="h-4 w-4 mr-2" />
                Düzenle
              </Button>
              <Button
                onClick={() => toast.info("PDF indirme özelliği yakında eklenecek")}
                className="bg-accent hover:bg-accent/90"
                data-testid="download-pdf-btn"
              >
                <Download className="h-4 w-4 mr-2" />
                PDF İndir
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Content */}
      <div className="container mx-auto px-6 py-8 max-w-5xl">
        <div className="space-y-8" data-testid="proposal-preview">
          {/* Cover */}
          <div className="aspect-[210/297] w-full">
            <ProposalCover proposal={proposal} />
          </div>

          {/* Content Pages */}
          <div className="bg-white text-gray-900 p-12 rounded shadow-2xl">
            <div className="space-y-8">
              {/* Header */}
              <div className="border-b-2 border-gray-200 pb-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">{proposal.proje_basligi}</h2>
                    <p className="text-sm text-gray-600">Teklif No: {proposal.teklif_no}</p>
                    <p className="text-sm text-gray-600">Tarih: {formatDate(proposal.tarih)}</p>
                  </div>
                  <img 
                    src="https://customer-assets.emergentagent.com/job_quote-creator-10/artifacts/mew65la4_logo%20sosn.jpg" 
                    alt="DEMART Logo" 
                    className="h-16 w-auto"
                  />
                </div>
              </div>

              {/* Customer Info */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Müşteri Bilgileri</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Firma:</span>
                    <p className="text-gray-900">{proposal.musteri_firma_adi}</p>
                  </div>
                  {proposal.musteri_yetkili && (
                    <div>
                      <span className="font-medium text-gray-700">Yetkili:</span>
                      <p className="text-gray-900">{proposal.musteri_yetkili}</p>
                    </div>
                  )}
                  {proposal.musteri_telefon && (
                    <div>
                      <span className="font-medium text-gray-700">Telefon:</span>
                      <p className="text-gray-900">{proposal.musteri_telefon}</p>
                    </div>
                  )}
                  {proposal.musteri_email && (
                    <div>
                      <span className="font-medium text-gray-700">E-posta:</span>
                      <p className="text-gray-900">{proposal.musteri_email}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Project Description */}
              {proposal.proje_aciklama && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">Proje Açıklaması</h3>
                  <p className="text-sm text-gray-700 leading-relaxed">{proposal.proje_aciklama}</p>
                </div>
              )}

              {/* Items Table */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Teklif Kalemleri</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-gray-300">
                      <th className="text-left py-2 font-bold text-gray-900">Açıklama</th>
                      <th className="text-center py-2 font-bold text-gray-900">Miktar</th>
                      <th className="text-center py-2 font-bold text-gray-900">Birim</th>
                      <th className="text-right py-2 font-bold text-gray-900">Birim Fiyat</th>
                      <th className="text-right py-2 font-bold text-gray-900">Toplam</th>
                    </tr>
                  </thead>
                  <tbody>
                    {proposal.kalemler.map((item, index) => (
                      <tr key={index} className="border-b border-gray-200">
                        <td className="py-3 text-gray-900">{item.aciklama}</td>
                        <td className="py-3 text-center text-gray-900">{item.miktar}</td>
                        <td className="py-3 text-center text-gray-900">{item.birim}</td>
                        <td className="py-3 text-right text-gray-900">{formatCurrency(item.birim_fiyat)}</td>
                        <td className="py-3 text-right font-semibold text-gray-900">{formatCurrency(item.toplam)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="border-t-2 border-gray-300">
                      <td colSpan="4" className="py-3 text-right font-bold text-gray-900">TOPLAM TUTAR:</td>
                      <td className="py-3 text-right font-bold text-2xl text-blue-600">{formatCurrency(proposal.toplam_tutar)}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              {/* Notes */}
              {proposal.notlar && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">Notlar ve Koşullar</h3>
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{proposal.notlar}</p>
                </div>
              )}

              {/* Footer */}
              <div className="border-t-2 border-gray-200 pt-6 mt-8">
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                  <div>
                    <p className="font-semibold text-gray-900">DEMART Mühendislik San. Tic. Ltd. Şti.</p>
                    <p>The Art of Design Engineering Maintenance</p>
                  </div>
                  <div className="text-right">
                    <p>Geçerlilik Süresi: {proposal.gecerlilik_suresi}</p>
                    <p>Teklif Tarihi: {formatDate(proposal.tarih)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProposalPreview;