#!/usr/bin/env python3
"""
CreateQuotation Page API Endpoint Tests
Testing critical endpoints for the CreateQuotation functionality
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

class CreateQuotationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_customer_id = None
        self.test_representative_id = None
        self.test_sales_product_id = None
        self.test_service_product_id = None
        
    def test_backend_connection(self):
        """Test if backend is accessible"""
        print_header("Testing Backend Connection")
        try:
            response = self.session.get(f"{API_BASE}/statistics")
            if response.status_code == 200:
                print_success(f"Backend is accessible at {API_BASE}")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Cannot connect to backend: {str(e)}")
            return False

    def setup_test_data(self):
        """Create test data needed for quotation creation"""
        print_header("Setting Up Test Data")
        
        # Create test customer
        import random
        unique_tax_number = f"{random.randint(1000000000, 9999999999)}"
        
        customer_data = {
            "name": "Test Müşteri A.Ş.",
            "contact_person": "Ahmet Yılmaz",
            "email": "ahmet.yilmaz@testmusteri.com",
            "phone": "+90 212 555 0100",
            "address": "Levent Mahallesi, İş Kuleleri No:1",
            "city": "İstanbul",
            "country": "Türkiye",
            "tax_office": "Beşiktaş Vergi Dairesi",
            "tax_number": unique_tax_number
        }
        
        try:
            response = self.session.post(f"{API_BASE}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                self.test_customer_id = customer['id']
                print_success(f"Test customer created: {customer['name']}")
            else:
                print_error(f"Failed to create test customer: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating test customer: {str(e)}")
            return False

        # Create test representative
        rep_data = {
            "name": "Mehmet Özkan",
            "phone": "+90 532 123 4567",
            "email": "mehmet.ozkan@demart.com",
            "department": "Satış"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/representatives", json=rep_data)
            if response.status_code == 200:
                rep = response.json()
                self.test_representative_id = rep['id']
                print_success(f"Test representative created: {rep['name']}")
            else:
                print_error(f"Failed to create test representative: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating test representative: {str(e)}")
            return False

        # Create test sales product
        sales_product_data = {
            "product_type": "sales",
            "brand": "DEMART",
            "model": "DM-2025",
            "item_short_name": "Endüstriyel Pompa",
            "item_description": "Yüksek basınçlı endüstriyel pompa sistemi",
            "default_unit": "Adet",
            "default_currency": "EUR",
            "default_unit_price": 2500.0,
            "cost_price": 2000.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/products", json=sales_product_data)
            if response.status_code == 200:
                product = response.json()
                self.test_sales_product_id = product['id']
                print_success(f"Test sales product created: {product['item_short_name']}")
            else:
                print_error(f"Failed to create test sales product: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating test sales product: {str(e)}")
            return False

        # Create test service product
        service_product_data = {
            "product_type": "service",
            "brand": "DEMART",
            "model": "SRV-001",
            "item_short_name": "Bakım Hizmeti",
            "item_description": "Yıllık bakım ve onarım hizmeti",
            "default_unit": "Saat",
            "default_currency": "TRY",
            "default_unit_price": 150.0,
            "cost_price": 100.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/products", json=service_product_data)
            if response.status_code == 200:
                product = response.json()
                self.test_service_product_id = product['id']
                print_success(f"Test service product created: {product['item_short_name']}")
            else:
                print_error(f"Failed to create test service product: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating test service product: {str(e)}")
            return False

        return True

    def test_get_active_customers(self):
        """Test GET /api/customers?is_active=true"""
        print_header("Test 1: GET /api/customers?is_active=true")
        
        try:
            response = self.session.get(f"{API_BASE}/customers?is_active=true")
            
            if response.status_code != 200:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
            
            customers = response.json()
            
            # Check if response is array
            if not isinstance(customers, list):
                print_error("Response is not an array")
                return False
            
            print_success(f"Response is array with {len(customers)} customers")
            
            if len(customers) == 0:
                print_warning("No active customers found")
                return True
            
            # Check each customer has required fields
            for i, customer in enumerate(customers):
                if not isinstance(customer, dict):
                    print_error(f"Customer {i} is not an object")
                    return False
                
                # Check required fields
                if 'id' not in customer or not customer['id']:
                    print_error(f"Customer {i} missing 'id' field")
                    return False
                
                if 'name' not in customer or not customer['name']:
                    print_error(f"Customer {i} missing 'name' field")
                    return False
                
                print_success(f"Customer {i}: ID={customer['id']}, Name={customer['name']}")
            
            print_success("All customers have required fields (id, name)")
            return True
            
        except Exception as e:
            print_error(f"Error testing customers endpoint: {str(e)}")
            return False

    def test_get_sales_products(self):
        """Test GET /api/products?product_type=sales&is_active=true"""
        print_header("Test 2: GET /api/products?product_type=sales&is_active=true")
        
        try:
            response = self.session.get(f"{API_BASE}/products?product_type=sales&is_active=true")
            
            if response.status_code != 200:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
            
            products = response.json()
            
            # Check if response is array
            if not isinstance(products, list):
                print_error("Response is not an array")
                return False
            
            print_success(f"Response is array with {len(products)} sales products")
            
            if len(products) == 0:
                print_warning("No active sales products found")
                return True
            
            # Check product_type parameter is working
            for i, product in enumerate(products):
                if product.get('product_type') != 'sales':
                    print_error(f"Product {i} has wrong product_type: {product.get('product_type')}")
                    return False
            
            print_success("All products have correct product_type=sales")
            
            # Check each product has required fields
            required_fields = ['id', 'brand', 'model', 'item_short_name', 'default_unit', 'default_currency', 'default_unit_price']
            
            for i, product in enumerate(products):
                if not isinstance(product, dict):
                    print_error(f"Product {i} is not an object")
                    return False
                
                for field in required_fields:
                    if field not in product:
                        print_error(f"Product {i} missing '{field}' field")
                        return False
                    
                    if product[field] is None or product[field] == "":
                        print_error(f"Product {i} has empty '{field}' field")
                        return False
                
                print_success(f"Product {i}: {product['brand']} {product['model']} - {product['item_short_name']}")
            
            print_success("All sales products have required fields")
            return True
            
        except Exception as e:
            print_error(f"Error testing sales products endpoint: {str(e)}")
            return False

    def test_get_service_products(self):
        """Test GET /api/products?product_type=service&is_active=true"""
        print_header("Test 3: GET /api/products?product_type=service&is_active=true")
        
        try:
            response = self.session.get(f"{API_BASE}/products?product_type=service&is_active=true")
            
            if response.status_code != 200:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
            
            products = response.json()
            
            # Check if response is array
            if not isinstance(products, list):
                print_error("Response is not an array")
                return False
            
            print_success(f"Response is array with {len(products)} service products")
            
            if len(products) == 0:
                print_warning("No active service products found")
                return True
            
            # Check product_type parameter is working
            for i, product in enumerate(products):
                if product.get('product_type') != 'service':
                    print_error(f"Product {i} has wrong product_type: {product.get('product_type')}")
                    return False
            
            print_success("All products have correct product_type=service")
            
            # Check each product has required fields
            required_fields = ['id', 'brand', 'model', 'item_short_name', 'default_unit', 'default_currency', 'default_unit_price']
            
            for i, product in enumerate(products):
                if not isinstance(product, dict):
                    print_error(f"Product {i} is not an object")
                    return False
                
                for field in required_fields:
                    if field not in product:
                        print_error(f"Product {i} missing '{field}' field")
                        return False
                    
                    if product[field] is None or product[field] == "":
                        print_error(f"Product {i} has empty '{field}' field")
                        return False
                
                print_success(f"Product {i}: {product['brand']} {product['model']} - {product['item_short_name']}")
            
            print_success("All service products have required fields")
            return True
            
        except Exception as e:
            print_error(f"Error testing service products endpoint: {str(e)}")
            return False

    def test_get_active_representatives(self):
        """Test GET /api/representatives?is_active=true"""
        print_header("Test 4: GET /api/representatives?is_active=true")
        
        try:
            response = self.session.get(f"{API_BASE}/representatives?is_active=true")
            
            if response.status_code != 200:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
            
            representatives = response.json()
            
            # Check if response is array
            if not isinstance(representatives, list):
                print_error("Response is not an array")
                return False
            
            print_success(f"Response is array with {len(representatives)} representatives")
            
            if len(representatives) == 0:
                print_warning("No active representatives found")
                return True
            
            # Check each representative has required fields
            for i, rep in enumerate(representatives):
                if not isinstance(rep, dict):
                    print_error(f"Representative {i} is not an object")
                    return False
                
                # Check required fields
                required_fields = ['id', 'name', 'phone']
                for field in required_fields:
                    if field not in rep or not rep[field]:
                        print_error(f"Representative {i} missing '{field}' field")
                        return False
                
                print_success(f"Representative {i}: ID={rep['id']}, Name={rep['name']}, Phone={rep['phone']}")
            
            print_success("All representatives have required fields (id, name, phone)")
            return True
            
        except Exception as e:
            print_error(f"Error testing representatives endpoint: {str(e)}")
            return False

    def test_create_sales_quotation(self):
        """Test POST /api/quotations (Sales)"""
        print_header("Test 5: POST /api/quotations (Sales)")
        
        if not self.test_customer_id or not self.test_representative_id:
            print_error("Test data not available for quotation creation")
            return False
        
        quotation_data = {
            "quotation_type": "sales",
            "customer_id": self.test_customer_id,
            "representative_id": self.test_representative_id,
            "subject": "Test Satış Teklifi",
            "validity_days": 30,
            "language": "turkish",
            "line_items": []
        }
        
        try:
            response = self.session.post(f"{API_BASE}/quotations", json=quotation_data)
            
            if response.status_code != 200:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
            
            quotation = response.json()
            
            # Check if response is object
            if not isinstance(quotation, dict):
                print_error("Response is not an object")
                return False
            
            print_success("Response is a valid object")
            
            # Check required fields
            required_fields = ['id', 'quotation_type', 'customer_id', 'subject', 'quote_no']
            for field in required_fields:
                if field not in quotation:
                    print_error(f"Response missing '{field}' field")
                    return False
                
                if quotation[field] is None or quotation[field] == "":
                    print_error(f"Response has empty '{field}' field")
                    return False
            
            print_success("All required fields are present and non-empty")
            
            # Validate specific values
            if quotation['quotation_type'] != 'sales':
                print_error(f"Wrong quotation_type: {quotation['quotation_type']}")
                return False
            
            if quotation['customer_id'] != self.test_customer_id:
                print_error(f"Wrong customer_id: {quotation['customer_id']}")
                return False
            
            if quotation['subject'] != "Test Satış Teklifi":
                print_error(f"Wrong subject: {quotation['subject']}")
                return False
            
            print_success(f"Sales quotation created successfully: {quotation['quote_no']}")
            print_info(f"Quotation ID: {quotation['id']}")
            print_info(f"Quote Number: {quotation['quote_no']}")
            
            return True
            
        except Exception as e:
            print_error(f"Error testing sales quotation creation: {str(e)}")
            return False

    def test_create_service_quotation(self):
        """Test POST /api/quotations (Service)"""
        print_header("Test 6: POST /api/quotations (Service)")
        
        if not self.test_customer_id or not self.test_representative_id:
            print_error("Test data not available for quotation creation")
            return False
        
        quotation_data = {
            "quotation_type": "service",
            "customer_id": self.test_customer_id,
            "representative_id": self.test_representative_id,
            "subject": "Test Servis Teklifi",
            "validity_days": 30,
            "language": "turkish",
            "line_items": []
        }
        
        try:
            response = self.session.post(f"{API_BASE}/quotations", json=quotation_data)
            
            if response.status_code != 200:
                print_error(f"API returned status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
            
            quotation = response.json()
            
            # Check if response is object
            if not isinstance(quotation, dict):
                print_error("Response is not an object")
                return False
            
            print_success("Response is a valid object")
            
            # Check required fields
            required_fields = ['id', 'quotation_type', 'customer_id', 'subject', 'quote_no']
            for field in required_fields:
                if field not in quotation:
                    print_error(f"Response missing '{field}' field")
                    return False
                
                if quotation[field] is None or quotation[field] == "":
                    print_error(f"Response has empty '{field}' field")
                    return False
            
            print_success("All required fields are present and non-empty")
            
            # Validate specific values
            if quotation['quotation_type'] != 'service':
                print_error(f"Wrong quotation_type: {quotation['quotation_type']}")
                return False
            
            if quotation['customer_id'] != self.test_customer_id:
                print_error(f"Wrong customer_id: {quotation['customer_id']}")
                return False
            
            if quotation['subject'] != "Test Servis Teklifi":
                print_error(f"Wrong subject: {quotation['subject']}")
                return False
            
            print_success(f"Service quotation created successfully: {quotation['quote_no']}")
            print_info(f"Quotation ID: {quotation['id']}")
            print_info(f"Quote Number: {quotation['quote_no']}")
            
            return True
            
        except Exception as e:
            print_error(f"Error testing service quotation creation: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data"""
        print_header("Cleaning Up Test Data")
        
        # Deactivate test customer
        if self.test_customer_id:
            try:
                response = self.session.delete(f"{API_BASE}/customers/{self.test_customer_id}")
                if response.status_code == 200:
                    print_success("Test customer deactivated")
                else:
                    print_warning(f"Could not deactivate test customer: {response.status_code}")
            except Exception as e:
                print_warning(f"Error deactivating customer: {str(e)}")

    def run_all_tests(self):
        """Run all CreateQuotation API tests"""
        print_header("CreateQuotation Page API Endpoint Tests")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        # Test 0: Backend Connection
        test_results.append(("Backend Connection", self.test_backend_connection()))
        
        # Setup test data
        setup_success = self.setup_test_data()
        test_results.append(("Setup Test Data", setup_success))
        
        if not setup_success:
            print_error("Cannot continue tests without test data")
            self.print_test_summary(test_results)
            return False
        
        # Test 1: GET /api/customers?is_active=true
        test_results.append(("GET Active Customers", self.test_get_active_customers()))
        
        # Test 2: GET /api/products?product_type=sales&is_active=true
        test_results.append(("GET Sales Products", self.test_get_sales_products()))
        
        # Test 3: GET /api/products?product_type=service&is_active=true
        test_results.append(("GET Service Products", self.test_get_service_products()))
        
        # Test 4: GET /api/representatives?is_active=true
        test_results.append(("GET Active Representatives", self.test_get_active_representatives()))
        
        # Test 5: POST /api/quotations (Sales)
        test_results.append(("POST Sales Quotation", self.test_create_sales_quotation()))
        
        # Test 6: POST /api/quotations (Service)
        test_results.append(("POST Service Quotation", self.test_create_service_quotation()))
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print Summary
        self.print_test_summary(test_results)
        
        return all(result for _, result in test_results)
    
    def print_test_summary(self, test_results):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            if result:
                print_success(f"{test_name}: PASSED")
                passed += 1
            else:
                print_error(f"{test_name}: FAILED")
                failed += 1
        
        print(f"\n{Colors.BOLD}Total Tests: {len(test_results)}{Colors.ENDC}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {failed}{Colors.ENDC}")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED ❌{Colors.ENDC}")

def main():
    """Main function"""
    tester = CreateQuotationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()