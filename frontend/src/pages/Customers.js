import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ArrowLeft, Plus, Edit, Trash2, Building2 } from "lucide-react";
import { toast } from "sonner";
import { useTranslation } from "@/i18n/translations";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Customers = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    contact_person: "",
    contacts: [],
    email: "",
    phone: "",
    address: "",
    city: "",
    country: "Türkiye",
    tax_office: "",
    tax_number: "",
    note: ""
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers?is_active=true`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
      toast.error("Failed to load customers");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingCustomer) {
        await axios.put(`${API}/customers/${editingCustomer.id}`, formData);
        toast.success(t('customerUpdated'));
      } else {
        await axios.post(`${API}/customers`, formData);
        toast.success(t('customerCreated'));
      }
      
      setDialogOpen(false);
      resetForm();
      fetchCustomers();
    } catch (error) {
      console.error("Error saving customer:", error);
      toast.error(error.response?.data?.detail || t('customerSaveFailed'));
    }
  };

  const handleEdit = (customer) => {
    setEditingCustomer(customer);
    setFormData({
      name: customer.name || "",
      contact_person: customer.contact_person || "",
      contacts: customer.contacts || [],
      email: customer.email || "",
      phone: customer.phone || "",
      address: customer.address || "",
      city: customer.city || "",
      country: customer.country || "Türkiye",
      tax_office: customer.tax_office || "",
      tax_number: customer.tax_number || "",
      note: customer.note || ""
    });
    setDialogOpen(true);
  };

  const handleDelete = async (customerId, customerName) => {
    try {
      const quotationsResponse = await axios.get(`${API}/quotations`);
      const customerQuotations = quotationsResponse.data.filter(
        q => q.customer_id === customerId
      );

      if (customerQuotations.length > 0) {
        const firstConfirm = window.confirm(
          `${t('warning')} ${t('attention')}\n\n` +
          `"${customerName}" ${t('confirmDeleteCustomerWithQuotations').replace('adet', customerQuotations.length)}`
        );

        if (!firstConfirm) return;

        const secondConfirm = window.confirm(
          `${t('warning')} ${t('finalWarning')}\n\n` +
          `${t('cannotBeUndone')}\n\n` +
          `"${customerName}" ${t('confirmDeleteCustomerFinal').replace('adet', customerQuotations.length)}`
        );

        if (!secondConfirm) return;
      } else {
        const confirm = window.confirm(
          `"${customerName}" ${t('confirmDeleteCustomerSimple')}`
        );
        if (!confirm) return;
      }

      await axios.delete(`${API}/customers/${customerId}`);
      toast.success(`${customerName} ${t('customerDeleted')}`);
      fetchCustomers();
    } catch (error) {
      console.error("Error deleting customer:", error);
      toast.error(t('customerDeleteFailed'));
    }
  };

  const resetForm = () => {
    setEditingCustomer(null);
    setFormData({
      name: "",
      contact_person: "",
      contacts: [],
      email: "",
      phone: "",
      address: "",
      city: "",
      country: "Türkiye",
      tax_office: "",
      tax_number: "",
      note: ""
    });
  };

  const addContact = () => {
    setFormData({
      ...formData,
      contacts: [
        ...formData.contacts,
        { name: "", title: "", email: "", phone: "", is_primary: false }
      ]
    });
  };

  const removeContact = (index) => {
    setFormData({
      ...formData,
      contacts: formData.contacts.filter((_, i) => i !== index)
    });
  };

  const updateContact = (index, field, value) => {
    const updatedContacts = [...formData.contacts];
    updatedContacts[index] = { ...updatedContacts[index], [field]: value };
    setFormData({ ...formData, contacts: updatedContacts });
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-heading font-bold">{t('customers')}</h1>
                <p className="text-xs text-muted-foreground">{t('manageCustomerDatabase')}</p>
              </div>
            </div>
            <Dialog 
              open={dialogOpen} 
              onOpenChange={(open) => { 
                if (!open) {
                  const confirmed = window.confirm(t('confirmDeleteUnsaved'));
                  if (confirmed) {
                    setDialogOpen(false);
                    resetForm();
                  }
                } else {
                  setDialogOpen(open);
                }
              }}
            >
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  {t('addCustomer')}
                </Button>
              </DialogTrigger>
              <DialogContent 
                className="max-w-3xl max-h-[90vh] overflow-y-auto"
                onPointerDownOutside={(e) => e.preventDefault()}
                onEscapeKeyDown={(e) => e.preventDefault()}
              >
                <DialogHeader>
                  <DialogTitle>{editingCustomer ? t('editCustomer') : t('addCustomer')}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 mt-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <Label>{t('companyName')} *</Label>
                      <Input
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label>{t('address')}</Label>
                      <Textarea
                        value={formData.address}
                        onChange={(e) => setFormData({...formData, address: e.target.value})}
                        rows={2}
                      />
                    </div>
                    <div>
                      <Label>{t('city')}</Label>
                      <Input
                        value={formData.city}
                        onChange={(e) => setFormData({...formData, city: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label>{t('country')}</Label>
                      <Input
                        value={formData.country}
                        onChange={(e) => setFormData({...formData, country: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label>{t('taxOffice')}</Label>
                      <Input
                        value={formData.tax_office}
                        onChange={(e) => setFormData({...formData, tax_office: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label>{t('taxNumber')}</Label>
                      <Input
                        value={formData.tax_number}
                        onChange={(e) => setFormData({...formData, tax_number: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between mb-3">
                      <Label className="text-lg font-semibold">{t('contactPersons')}</Label>
                      <Button type="button" variant="outline" size="sm" onClick={addContact}>
                        <Plus className="h-4 w-4 mr-2" />
                        {t('addContact')}
                      </Button>
                    </div>
                    
                    {formData.contacts.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-4 border rounded">
                        {t('addContactPerson')}
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {formData.contacts.map((contact, index) => (
                          <div key={index} className="p-4 border rounded bg-muted/20">
                            <div className="flex items-center justify-between mb-3">
                              <span className="text-sm font-medium">{t('contact')} {index + 1}</span>
                              <Button type="button" variant="ghost" size="sm" onClick={() => removeContact(index)}>
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <Label>{t('name')} *</Label>
                                <Input
                                  value={contact.name}
                                  onChange={(e) => updateContact(index, 'name', e.target.value)}
                                  required
                                />
                              </div>
                              <div>
                                <Label>{t('title')}</Label>
                                <Input
                                  value={contact.title || ''}
                                  onChange={(e) => updateContact(index, 'title', e.target.value)}
                                  placeholder={t('placeholderTitle')}
                                />
                              </div>
                              <div>
                                <Label>{t('email')}</Label>
                                <Input
                                  type="email"
                                  value={contact.email || ''}
                                  onChange={(e) => updateContact(index, 'email', e.target.value)}
                                />
                              </div>
                              <div>
                                <Label>{t('phone')}</Label>
                                <Input
                                  value={contact.phone || ''}
                                  onChange={(e) => updateContact(index, 'phone', e.target.value)}
                                />
                              </div>
                              <div className="col-span-2">
                                <label className="flex items-center gap-2">
                                  <input
                                    type="checkbox"
                                    checked={contact.is_primary || false}
                                    onChange={(e) => updateContact(index, 'is_primary', e.target.checked)}
                                  />
                                  <span className="text-sm">{t('primaryContact')}</span>
                                </label>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>{t('notes')}</Label>
                    <Textarea
                      value={formData.note}
                      onChange={(e) => setFormData({...formData, note: e.target.value})}
                      rows={3}
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>{t('cancel')}</Button>
                    <Button type="submit">{t('save')}</Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-12">{t('loading')}</div>
        ) : customers.length === 0 ? (
          <Card className="p-12 text-center">
            <Building2 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">{t('noCustomersYet')}</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customers.map((customer) => (
              <Card key={customer.id} className="p-4 bg-card border border-border/40 hover:border-primary/50 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">{customer.name}</h3>
                    {customer.city && <p className="text-sm text-muted-foreground">{customer.city}, {customer.country}</p>}
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => handleEdit(customer)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => handleDelete(customer.id, customer.name)}
                      className="hover:bg-destructive/10 hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="space-y-1 text-xs text-muted-foreground">
                  {customer.contacts && customer.contacts.length > 0 ? (
                    <div>
                      <span className="font-semibold">{t('contacts')}: {customer.contacts.length}</span>
                      <div className="ml-2 mt-1 space-y-1">
                        {customer.contacts.slice(0, 2).map((contact, idx) => (
                          <div key={idx} className="text-xs">
                            • {contact.name} {contact.title && `(${contact.title})`}
                          </div>
                        ))}
                        {customer.contacts.length > 2 && (
                          <div className="text-xs italic">...{t('andMore')} {customer.contacts.length - 2} {t('andMore')}</div>
                        )}
                      </div>
                    </div>
                  ) : (
                    customer.contact_person && <div>👤 {customer.contact_person}</div>
                  )}
                  {customer.email && <div>📧 {customer.email}</div>}
                  {customer.phone && <div>📱 {customer.phone}</div>}
                  {customer.tax_number && <div>🏢 {customer.tax_number}</div>}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Customers;