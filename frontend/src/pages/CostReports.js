import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { ArrowLeft, BarChart3, Lock, Calendar } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CostReports = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    quotation_type: "",
    category_id: ""
  });
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetchCategories();
    fetchReports();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/cost-categories`);
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.quotation_type) params.append('quotation_type', filters.quotation_type);
      if (filters.category_id) params.append('category_id', filters.category_id);
      
      const response = await axios.get(`${API}/cost-reports?${params.toString()}`);
      setReports(response.data);
    } catch (error) {
      console.error("Error fetching reports:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const formatCurrency = (amount, currency) => {
    return `${amount.toFixed(2)} ${currency}`;
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-heading font-bold flex items-center gap-2">
                <Lock className="h-6 w-6 text-red-400" />
                Cost Reports (SECRET)
              </h1>
              <p className="text-xs text-muted-foreground">Internal cost analysis - Private</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Filters */}
        <Card className="p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <Label>Start Date</Label>
              <div className="relative">
                <input
                  type="date"
                  name="start_date"
                  value={filters.start_date}
                  onChange={handleFilterChange}
                  className="w-full p-2 pr-10 border rounded bg-background text-foreground cursor-pointer hover:border-primary focus:border-primary focus:ring-1 focus:ring-primary"
                />
                <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-blue-500 pointer-events-none" />
              </div>
            </div>
            <div>
              <Label>End Date</Label>
              <div className="relative">
                <input
                  type="date"
                  name="end_date"
                  value={filters.end_date}
                  onChange={handleFilterChange}
                  className="w-full p-2 pr-10 border rounded bg-background text-foreground cursor-pointer hover:border-primary focus:border-primary focus:ring-1 focus:ring-primary"
                />
                <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-blue-500 pointer-events-none" />
              </div>
            </div>
            <div>
              <Label>Type</Label>
              <select
                name="quotation_type"
                value={filters.quotation_type}
                onChange={handleFilterChange}
                className="w-full p-2 border rounded bg-background"
              >
                <option value="">All</option>
                <option value="sales">Sales</option>
                <option value="service">Service</option>
              </select>
            </div>
            <div>
              <Label>Category</Label>
              <select
                name="category_id"
                value={filters.category_id}
                onChange={handleFilterChange}
                className="w-full p-2 border rounded bg-background"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-4">
            <Button onClick={fetchReports} disabled={loading}>
              <BarChart3 className="h-4 w-4 mr-2" />
              {loading ? "Loading..." : "Generate Report"}
            </Button>
          </div>
        </Card>

        {/* Reports */}
        {reports && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Cost Breakdown by Category</h2>
              <div className="text-sm text-muted-foreground">
                Total items: {reports.total_items}
              </div>
            </div>

            {Object.keys(reports.reports).length === 0 ? (
              <Card className="p-12 text-center">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No cost data found for selected filters</p>
              </Card>
            ) : (
              Object.keys(reports.reports).map(categoryName => (
                <Card key={categoryName} className="p-6">
                  <h3 className="text-lg font-semibold mb-4 text-foreground">{categoryName}</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {Object.keys(reports.reports[categoryName]).map(currency => (
                      <div key={currency} className="p-4 bg-muted/20 rounded">
                        <div className="text-xs text-muted-foreground mb-1">{currency}</div>
                        <div className="text-2xl font-bold text-red-400 font-mono">
                          {formatCurrency(reports.reports[categoryName][currency], currency)}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))
            )}

            {/* Grand Totals */}
            {Object.keys(reports.reports).length > 0 && (
              <Card className="p-6 bg-red-500/10 border-red-500/30">
                <h3 className="text-lg font-semibold mb-4">Grand Total - All Categories</h3>
                <div className="grid grid-cols-3 gap-4">
                  {(() => {
                    const grandTotals = {};
                    Object.values(reports.reports).forEach(categoryData => {
                      Object.keys(categoryData).forEach(currency => {
                        grandTotals[currency] = (grandTotals[currency] || 0) + categoryData[currency];
                      });
                    });
                    return Object.keys(grandTotals).map(currency => (
                      <div key={currency} className="p-4 bg-background rounded">
                        <div className="text-xs text-muted-foreground mb-1">{currency}</div>
                        <div className="text-3xl font-bold text-red-400 font-mono">
                          {formatCurrency(grandTotals[currency], currency)}
                        </div>
                      </div>
                    ));
                  })()}
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CostReports;
