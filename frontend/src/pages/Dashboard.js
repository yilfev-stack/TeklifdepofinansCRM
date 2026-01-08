import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Plus, FileText, Eye, Edit, Trash2, Calendar, Building2 } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    try {
      const response = await axios.get(`${API}/proposals`);
      setProposals(response.data);
    } catch (error) {
      console.error("Teklifler yüklenirken hata:", error);
      toast.error("Teklifler yüklenemedi");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bu teklifi silmek istediğinizden emin misiniz?")) return;
    
    try {
      await axios.delete(`${API}/proposals/${id}`);
      toast.success("Teklif silindi");
      fetchProposals();
    } catch (error) {
      console.error("Teklif silinirken hata:", error);
      toast.error("Teklif silinemedi");
    }
  };

  const getStatusBadge = (durum) => {
    const styles = {
      taslak: "bg-muted text-muted-foreground",
      gonderildi: "bg-blue-500/20 text-blue-400 border border-blue-500/30",
      onaylandi: "bg-green-500/20 text-green-400 border border-green-500/30",
      reddedildi: "bg-red-500/20 text-red-400 border border-red-500/30"
    };
    
    const labels = {
      taslak: "Taslak",
      gonderildi: "Gönderildi",
      onaylandi: "Onaylandı",
      reddedildi: "Reddedildi"
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-mono uppercase tracking-wider ${styles[durum]}`}>
        {labels[durum]}
      </span>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(amount);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_quote-creator-10/artifacts/mew65la4_logo%20sosn.jpg" 
                alt="DEMART Logo" 
                className="h-12 w-auto"
              />
              <div>
                <h1 className="text-3xl font-heading font-bold tracking-tight text-foreground">
                  QuoteOS
                </h1>
                <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
                  Teklif Yönetim Sistemi
                </p>
              </div>
            </div>
            <Button 
              onClick={() => navigate('/create')} 
              className="bg-primary hover:bg-primary/90 shadow-[0_0_20px_rgba(0,82,204,0.3)] transition-all duration-300 font-medium"
              data-testid="create-proposal-btn"
            >
              <Plus className="mr-2 h-4 w-4" />
              Yeni Teklif Oluştur
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4 bg-card border border-border/40 hover:border-primary/50 transition-colors duration-300">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">Toplam Teklif</div>
            <div className="text-3xl font-bold text-foreground">{proposals.length}</div>
          </Card>
          <Card className="p-4 bg-card border border-border/40 hover:border-primary/50 transition-colors duration-300">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">Taslak</div>
            <div className="text-3xl font-bold text-foreground">
              {proposals.filter(p => p.durum === 'taslak').length}
            </div>
          </Card>
          <Card className="p-4 bg-card border border-border/40 hover:border-primary/50 transition-colors duration-300">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">Gönderildi</div>
            <div className="text-3xl font-bold text-foreground">
              {proposals.filter(p => p.durum === 'gonderildi').length}
            </div>
          </Card>
          <Card className="p-4 bg-card border border-border/40 hover:border-primary/50 transition-colors duration-300">
            <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">Onaylandı</div>
            <div className="text-3xl font-bold text-green-400">
              {proposals.filter(p => p.durum === 'onaylandi').length}
            </div>
          </Card>
        </div>

        {/* Proposals List */}
        <div className="space-y-4" data-testid="proposals-list">
          <h2 className="text-2xl font-heading font-bold tracking-tight text-foreground/90 mb-6">Tüm Teklifler</h2>
          
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Yükleniyor...</div>
          ) : proposals.length === 0 ? (
            <Card className="p-12 text-center bg-card border border-border/40">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-4">Henüz teklif oluşturulmamış</p>
              <Button onClick={() => navigate('/create')} data-testid="empty-create-proposal-btn">
                <Plus className="mr-2 h-4 w-4" />
                İlk Teklifi Oluştur
              </Button>
            </Card>
          ) : (
            proposals.map((proposal) => (
              <Card 
                key={proposal.id} 
                className="p-6 bg-card border border-border/40 hover:border-primary/50 transition-all duration-300 group"
                data-testid={`proposal-card-${proposal.id}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-xs font-mono uppercase tracking-widest text-primary font-bold">
                        {proposal.teklif_no}
                      </span>
                      {getStatusBadge(proposal.durum)}
                    </div>
                    
                    <h3 className="text-xl font-heading font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                      {proposal.proje_basligi}
                    </h3>
                    
                    <div className="flex items-center gap-6 text-sm text-muted-foreground mb-3">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        <span>{proposal.musteri_firma_adi}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(proposal.tarih)}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">Toplam:</span>
                      <span className="text-2xl font-bold text-accent font-mono">
                        {formatCurrency(proposal.toplam_tutar)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => navigate(`/preview/${proposal.id}`)}
                      className="hover:bg-primary/10 hover:text-primary"
                      data-testid={`preview-btn-${proposal.id}`}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => navigate(`/edit/${proposal.id}`)}
                      className="hover:bg-primary/10 hover:text-primary"
                      data-testid={`edit-btn-${proposal.id}`}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(proposal.id)}
                      className="hover:bg-destructive/10 hover:text-destructive"
                      data-testid={`delete-btn-${proposal.id}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;