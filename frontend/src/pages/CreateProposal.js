import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Plus, Trash2, Save } from "lucide-react";
import { toast } from "sonner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CreateProposal = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    teklif_no: `TKL-${Date.now().toString().slice(-8)}`,
    musteri_firma_adi: "",
    musteri_yetkili: "",
    musteri_telefon: "",
    musteri_email: "",
    proje_basligi: "",
    proje_aciklama: "",
    gecerlilik_suresi: "30 gün",
    notlar: "",
    durum: "taslak",
    kalemler: [
      { aciklama: "", miktar: 1, birim: "Adet", birim_fiyat: 0, toplam: 0 }
    ]
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleItemChange = (index, field, value) => {
    const newKalemler = [...formData.kalemler];
    newKalemler[index][field] = value;
    
    // Toplam hesapla
    if (field === 'miktar' || field === 'birim_fiyat') {
      const miktar = parseFloat(newKalemler[index].miktar) || 0;
      const birim_fiyat = parseFloat(newKalemler[index].birim_fiyat) || 0;
      newKalemler[index].toplam = miktar * birim_fiyat;
    }
    
    setFormData(prev => ({ ...prev, kalemler: newKalemler }));
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      kalemler: [...prev.kalemler, { aciklama: "", miktar: 1, birim: "Adet", birim_fiyat: 0, toplam: 0 }]
    }));
  };

  const removeItem = (index) => {
    if (formData.kalemler.length === 1) {
      toast.error("En az bir kalem olmalıdır");
      return;
    }
    setFormData(prev => ({
      ...prev,
      kalemler: prev.kalemler.filter((_, i) => i !== index)
    }));
  };

  const calculateTotal = () => {
    return formData.kalemler.reduce((sum, item) => sum + (item.toplam || 0), 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.musteri_firma_adi || !formData.proje_basligi) {
      toast.error("Lütfen zorunlu alanları doldurun");
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${API}/proposals`, formData);
      toast.success("Teklif başarıyla oluşturuldu");
      navigate('/');
    } catch (error) {
      console.error("Teklif oluşturulurken hata:", error);
      toast.error("Teklif oluşturulamadı");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(amount);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
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
                Yeni Teklif Oluştur
              </h1>
              <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
                {formData.teklif_no}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="container mx-auto px-6 py-8 max-w-5xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Müşteri Bilgileri */}
          <Card className="p-6 bg-card border border-border/40">
            <h2 className="text-xl font-heading font-semibold text-foreground mb-4">Müşteri Bilgileri</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="musteri_firma_adi" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Firma Adı *
                </Label>
                <Input
                  id="musteri_firma_adi"
                  name="musteri_firma_adi"
                  value={formData.musteri_firma_adi}
                  onChange={handleInputChange}
                  required
                  className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                  data-testid="musteri-firma-input"
                />
              </div>
              <div>
                <Label htmlFor="musteri_yetkili" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Yetkili Kişi
                </Label>
                <Input
                  id="musteri_yetkili"
                  name="musteri_yetkili"
                  value={formData.musteri_yetkili}
                  onChange={handleInputChange}
                  className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                  data-testid="musteri-yetkili-input"
                />
              </div>
              <div>
                <Label htmlFor="musteri_telefon" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Telefon
                </Label>
                <Input
                  id="musteri_telefon"
                  name="musteri_telefon"
                  value={formData.musteri_telefon}
                  onChange={handleInputChange}
                  className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                  data-testid="musteri-telefon-input"
                />
              </div>
              <div>
                <Label htmlFor="musteri_email" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  E-posta
                </Label>
                <Input
                  id="musteri_email"
                  name="musteri_email"
                  type="email"
                  value={formData.musteri_email}
                  onChange={handleInputChange}
                  className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                  data-testid="musteri-email-input"
                />
              </div>
            </div>
          </Card>

          {/* Proje Bilgileri */}
          <Card className="p-6 bg-card border border-border/40">
            <h2 className="text-xl font-heading font-semibold text-foreground mb-4">Proje Bilgileri</h2>
            <div className="space-y-4">
              <div>
                <Label htmlFor="proje_basligi" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Proje Başlığı *
                </Label>
                <Input
                  id="proje_basligi"
                  name="proje_basligi"
                  value={formData.proje_basligi}
                  onChange={handleInputChange}
                  required
                  className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                  data-testid="proje-basligi-input"
                />
              </div>
              <div>
                <Label htmlFor="proje_aciklama" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  Proje Açıklaması
                </Label>
                <Textarea
                  id="proje_aciklama"
                  name="proje_aciklama"
                  value={formData.proje_aciklama}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                  data-testid="proje-aciklama-input"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="gecerlilik_suresi" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                    Geçerlilik Süresi
                  </Label>
                  <Input
                    id="gecerlilik_suresi"
                    name="gecerlilik_suresi"
                    value={formData.gecerlilik_suresi}
                    onChange={handleInputChange}
                    className="mt-1 bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
                    data-testid="gecerlilik-input"
                  />
                </div>
                <div>
                  <Label htmlFor="durum" className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                    Durum
                  </Label>
                  <Select value={formData.durum} onValueChange={(value) => setFormData(prev => ({ ...prev, durum: value }))}>
                    <SelectTrigger className="mt-1 bg-background border-input" data-testid="durum-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="z-50">
                      <SelectItem value="taslak" data-testid="durum-taslak">Taslak</SelectItem>
                      <SelectItem value="gonderildi" data-testid="durum-gonderildi">Gönderildi</SelectItem>
                      <SelectItem value="onaylandi" data-testid="durum-onaylandi">Onaylandı</SelectItem>
                      <SelectItem value="reddedildi" data-testid="durum-reddedildi">Reddedildi</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </Card>

          {/* Kalemler */}
          <Card className="p-6 bg-card border border-border/40">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-heading font-semibold text-foreground">Teklif Kalemleri</h2>
              <Button 
                type="button" 
                onClick={addItem} 
                size="sm"
                className="bg-primary hover:bg-primary/90"
                data-testid="add-item-btn"
              >
                <Plus className="h-4 w-4 mr-2" />
                Kalem Ekle
              </Button>
            </div>
            
            <div className="space-y-4">
              {formData.kalemler.map((item, index) => (
                <div key={index} className="p-4 bg-background/50 border border-border/40 rounded space-y-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                      Kalem {index + 1}
                    </span>
                    {formData.kalemler.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeItem(index)}
                        className="hover:bg-destructive/10 hover:text-destructive"
                        data-testid={`remove-item-btn-${index}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
                    <div className="md:col-span-5">
                      <Label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        Açıklama
                      </Label>
                      <Input
                        value={item.aciklama}
                        onChange={(e) => handleItemChange(index, 'aciklama', e.target.value)}
                        className="mt-1 bg-background border-input"
                        data-testid={`item-aciklama-${index}`}
                      />
                    </div>
                    <div className="md:col-span-2">
                      <Label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        Miktar
                      </Label>
                      <Input
                        type="number"
                        value={item.miktar}
                        onChange={(e) => handleItemChange(index, 'miktar', parseFloat(e.target.value))}
                        className="mt-1 bg-background border-input"
                        data-testid={`item-miktar-${index}`}
                      />
                    </div>
                    <div className="md:col-span-1">
                      <Label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        Birim
                      </Label>
                      <Input
                        value={item.birim}
                        onChange={(e) => handleItemChange(index, 'birim', e.target.value)}
                        className="mt-1 bg-background border-input"
                        data-testid={`item-birim-${index}`}
                      />
                    </div>
                    <div className="md:col-span-2">
                      <Label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        Birim Fiyat
                      </Label>
                      <Input
                        type="number"
                        value={item.birim_fiyat}
                        onChange={(e) => handleItemChange(index, 'birim_fiyat', parseFloat(e.target.value))}
                        className="mt-1 bg-background border-input"
                        data-testid={`item-birim-fiyat-${index}`}
                      />
                    </div>
                    <div className="md:col-span-2">
                      <Label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                        Toplam
                      </Label>
                      <div className="mt-1 px-3 py-2 bg-muted/20 border border-border/40 rounded text-accent font-mono font-bold">
                        {formatCurrency(item.toplam)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-4 border-t border-border/40 flex justify-between items-center">
              <span className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
                Toplam Tutar
              </span>
              <span className="text-3xl font-bold text-accent font-mono" data-testid="total-amount">
                {formatCurrency(calculateTotal())}
              </span>
            </div>
          </Card>

          {/* Notlar */}
          <Card className="p-6 bg-card border border-border/40">
            <h2 className="text-xl font-heading font-semibold text-foreground mb-4">Notlar</h2>
            <Textarea
              name="notlar"
              value={formData.notlar}
              onChange={handleInputChange}
              rows={4}
              placeholder="Ek notlar, koşullar veya açıklamalar..."
              className="bg-background border-input focus:border-primary focus:ring-1 focus:ring-primary"
              data-testid="notlar-input"
            />
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => navigate('/')}
              data-testid="cancel-btn"
            >
              İptal
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
              className="bg-primary hover:bg-primary/90 shadow-[0_0_20px_rgba(0,82,204,0.3)]"
              data-testid="save-proposal-btn"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? "Kaydediliyor..." : "Teklifi Kaydet"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProposal;