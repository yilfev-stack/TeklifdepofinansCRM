import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload, Download, Trash2, FileText, Image as ImageIcon, Receipt } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CATEGORIES = {
  incoming_costs: { 
    label: "Gelen Maliyetler (Bana Kesilen Faturalar)", 
    icon: Receipt,
    color: "text-red-600"
  },
  outgoing_costs: { 
    label: "Giden Maliyetler (Benim Kestiğim Fatura)", 
    icon: Receipt,
    color: "text-green-600"
  },
  images: { 
    label: "Resimler", 
    icon: ImageIcon,
    color: "text-blue-600"
  },
  received_quotes: { 
    label: "Aldığım Teklifler", 
    icon: FileText,
    color: "text-purple-600"
  }
};

const QuotationFiles = ({ quotationId }) => {
  const [files, setFiles] = useState({});
  const [uploading, setUploading] = useState(false);
  const fileInputRefs = useRef({});

  useEffect(() => {
    fetchFiles();
  }, [quotationId]);

  const fetchFiles = async () => {
    try {
      console.log('[QuotationFiles] Fetching files for quotation:', quotationId);
      const response = await axios.get(`${API}/quotations/${quotationId}/files`);
      console.log('[QuotationFiles] Received files:', response.data);
      
      // Group files by category
      const grouped = {};
      response.data.forEach(file => {
        console.log('[QuotationFiles] File category:', file.category, 'File:', file.original_filename);
        if (!grouped[file.category]) {
          grouped[file.category] = [];
        }
        grouped[file.category].push(file);
      });
      
      console.log('[QuotationFiles] Grouped files:', grouped);
      setFiles(grouped);
    } catch (error) {
      console.error("Error fetching files:", error);
      toast.error("Dosyalar yüklenemedi");
    }
  };

  const handleFileUpload = async (category, event) => {
    const uploadedFiles = Array.from(event.target.files);
    if (uploadedFiles.length === 0) return;

    console.log('====================================');
    console.log('[QuotationFiles] UPLOAD BAŞLADI');
    console.log('[QuotationFiles] Kategori:', category);
    console.log('[QuotationFiles] Dosya sayısı:', uploadedFiles.length);
    console.log('[QuotationFiles] Dosya isimleri:', uploadedFiles.map(f => f.name));
    console.log('====================================');

    setUploading(true);
    
    try {
      // Her dosyayı ayrı ayrı yükle
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const uploadUrl = `${API}/quotations/${quotationId}/files?category=${category}`;
        console.log('[QuotationFiles] Upload URL:', uploadUrl);
        console.log('[QuotationFiles] Yüklenen dosya:', file.name, 'Kategori:', category);
        
        const response = await axios.post(
          uploadUrl,
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" }
          }
        );
        
        console.log('[QuotationFiles] Upload response:', response.data);
        toast.success(`${file.name} yüklendi! (${category})`);
      }
      
      console.log('[QuotationFiles] Tüm dosyalar yüklendi, liste yenileniyor...');
      fetchFiles();
    } catch (error) {
      console.error("[QuotationFiles] Upload error:", error);
      console.error("[QuotationFiles] Error details:", error.response?.data);
      toast.error("Dosyalar yüklenemedi");
    } finally {
      setUploading(false);
      event.target.value = null;
    }
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const response = await axios.get(`${API}/files/${fileId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("Dosya indirildi!");
    } catch (error) {
      console.error("Error downloading file:", error);
      toast.error("Dosya indirilemedi");
    }
  };

  const handleDelete = async (fileId, filename) => {
    if (!window.confirm(`${filename} dosyasını silmek istediğinize emin misiniz?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/files/${fileId}`);
      toast.success("Dosya silindi");
      fetchFiles();
    } catch (error) {
      console.error("Error deleting file:", error);
      toast.error("Dosya silinemedi");
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dosya Yönetimi</h2>
      <p className="text-sm text-muted-foreground">
        Bu teklifle alakalı tüm dosyaları buradan yönetebilirsiniz. 
        Dosyalar bilgisayarınıza kaydedilir ve offline erişilebilir.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(CATEGORIES).map(([category, config]) => {
          const Icon = config.icon;
          const categoryFiles = files[category] || [];
          
          console.log(`[QuotationFiles RENDER] Kategori: ${category}, Dosya sayısı: ${categoryFiles.length}`);
          console.log(`[QuotationFiles RENDER] Dosyalar:`, categoryFiles.map(f => f.original_filename));
          
          return (
            <Card key={category} className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <Icon className={`h-6 w-6 ${config.color}`} />
                <h3 className="font-bold text-lg">{config.label} ({categoryFiles.length})</h3>
              </div>
              
              {/* Upload Button */}
              <div className="mb-4">
                <input
                  ref={el => fileInputRefs.current[category] = el}
                  type="file"
                  multiple
                  onChange={(e) => handleFileUpload(category, e)}
                  style={{ display: 'none' }}
                  disabled={uploading}
                />
                <Button 
                  variant="outline" 
                  className="w-full"
                  disabled={uploading}
                  onClick={() => fileInputRefs.current[category]?.click()}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  {uploading ? "Yükleniyor..." : "Dosya Yükle"}
                </Button>
              </div>

              {/* Files List */}
              <div className="space-y-2">
                {categoryFiles.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Henüz dosya yüklenmemiş
                  </p>
                ) : (
                  categoryFiles.map((file) => (
                    <div 
                      key={file.id} 
                      className="flex items-center justify-between p-3 border rounded hover:bg-accent"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {file.original_filename}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatFileSize(file.file_size)} • {new Date(file.uploaded_at).toLocaleDateString('tr-TR')}
                        </p>
                      </div>
                      <div className="flex gap-2 ml-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownload(file.id, file.original_filename)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(file.id, file.original_filename)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default QuotationFiles;