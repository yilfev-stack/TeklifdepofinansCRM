import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import Home from "@/pages/Home";
import Customers from "@/pages/Customers";
import Products from "@/pages/Products";
import Representatives from "@/pages/Representatives";
import QuotationsList from "@/pages/QuotationsList";
import CreateQuotation from "@/pages/CreateQuotation";
import EditQuotation from "@/pages/EditQuotation";
import QuotationPreview from "@/pages/QuotationPreview";
import CostReports from "@/pages/CostReports";
import Warehouse from "@/pages/Warehouse";
import Inventory from "@/pages/Inventory";
import RealCosts from "@/pages/RealCosts";
import SofisImport from "@/pages/SofisImport";
import "@/App.css";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/products" element={<Products />} />
          <Route path="/representatives" element={<Representatives />} />
          <Route path="/quotations/:type" element={<QuotationsList />} />
          <Route path="/quotations/:type/create" element={<CreateQuotation />} />
          <Route path="/quotations/:type/edit/:id" element={<EditQuotation />} />
          <Route path="/quotations/:type/preview/:id" element={<QuotationPreview />} />
          <Route path="/cost-reports" element={<CostReports />} />
          <Route path="/warehouse" element={<Warehouse />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/real-costs" element={<RealCosts />} />
          <Route path="/sofis-import" element={<SofisImport />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;