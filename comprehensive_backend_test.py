#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for DEMART Quotation Management System
Pre-deployment final testing including CRUD operations and endpoint health
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv
import random

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

class ComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_customer_id = None
        self.test_product_id = None
        self.test_quotation_id = None
        self.test_representative_id = None
        self.test_cost_category_id = None
        
    def test_database_connection(self):
        """Test MongoDB database connection"""
        print_header("Testing Database Connection")
        try:
            # Test statistics endpoint which queries multiple collections
            response = self.session.get(f"{API_BASE}/statistics")
            if response.status_code == 200:
                stats = response.json()
                print_success("Database connection is working")
                print_info(f"Statistics retrieved: {stats}")
                
                # Verify we can access different collections
                expected_keys = ['customers', 'products', 'sales_quotations', 'service_quotations']
                for key in expected_keys:
                    if key in stats:
                        print_success(f"Collection access verified: {key}")
                    else:
                        print_warning(f"Collection data not found: {key}")
                
                return True
            else:
                print_error(f"Database connection test failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Database connection error: {str(e)}")
            return False
    
    def test_customer_crud(self):
        """Test Customer CRUD operations"""
        print_header("Testing Customer CRUD Operations")
        
        # CREATE
        print_info("Testing Customer CREATE...")
        unique_tax_number = f"{random.randint(1000000000, 9999999999)}"
        customer_data = {
            "name": "Test Company CRUD Ltd",
            "contact_person": "Jane Doe",
            "email": "jane.doe@testcompany.com",
            "phone": "+90 212 555 9876",
            "address": "Test Address 456",
            "city": "Ankara",
            "country": "Turkey",
            "tax_office": "Ankara Vergi Dairesi",
            "tax_number": unique_tax_number
        }
        
        try:
            response = self.session.post(f"{API_BASE}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                self.test_customer_id = customer['id']
                print_success(f"Customer CREATE successful - ID: {self.test_customer_id}")
            else:
                print_error(f"Customer CREATE failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Customer CREATE error: {str(e)}")
            return False
        
        # READ (Single)
        print_info("Testing Customer READ (single)...")
        try:
            response = self.session.get(f"{API_BASE}/customers/{self.test_customer_id}")
            if response.status_code == 200:
                customer = response.json()
                if customer['name'] == customer_data['name']:
                    print_success("Customer READ (single) successful")
                else:
                    print_error("Customer READ data mismatch")
                    return False
            else:
                print_error(f"Customer READ failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Customer READ error: {str(e)}")
            return False
        
        # READ (List)
        print_info("Testing Customer READ (list)...")
        try:
            response = self.session.get(f"{API_BASE}/customers")
            if response.status_code == 200:
                customers = response.json()
                if isinstance(customers, list) and len(customers) > 0:
                    print_success(f"Customer READ (list) successful - Found {len(customers)} customers")
                else:
                    print_warning("Customer list is empty")
            else:
                print_error(f"Customer READ (list) failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Customer READ (list) error: {str(e)}")
            return False
        
        # UPDATE
        print_info("Testing Customer UPDATE...")
        update_data = {
            "name": "Updated Test Company CRUD Ltd",
            "email": "updated.jane@testcompany.com"
        }
        try:
            response = self.session.put(f"{API_BASE}/customers/{self.test_customer_id}", json=update_data)
            if response.status_code == 200:
                updated_customer = response.json()
                if updated_customer['name'] == update_data['name']:
                    print_success("Customer UPDATE successful")
                else:
                    print_error("Customer UPDATE data mismatch")
                    return False
            else:
                print_error(f"Customer UPDATE failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Customer UPDATE error: {str(e)}")
            return False
        
        # DELETE (Soft delete)
        print_info("Testing Customer DELETE (soft delete)...")
        try:
            response = self.session.delete(f"{API_BASE}/customers/{self.test_customer_id}")
            if response.status_code == 200:
                print_success("Customer DELETE successful")
                
                # Verify soft delete by checking is_active=false
                response = self.session.get(f"{API_BASE}/customers/{self.test_customer_id}")
                if response.status_code == 200:
                    customer = response.json()
                    if not customer.get('is_active', True):
                        print_success("Customer soft delete verified")
                    else:
                        print_warning("Customer may not be properly soft deleted")
                
            else:
                print_error(f"Customer DELETE failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Customer DELETE error: {str(e)}")
            return False
        
        return True
    
    def test_product_crud(self):
        """Test Product CRUD operations"""
        print_header("Testing Product CRUD Operations")
        
        # CREATE
        print_info("Testing Product CREATE...")
        product_data = {
            "product_type": "sales",
            "brand": "TestBrand",
            "model": "TestModel-X1",
            "category": "Industrial Equipment",
            "item_short_name": "Test Product CRUD",
            "item_description": "Test product for CRUD operations",
            "default_unit": "Pieces",
            "default_currency": "EUR",
            "default_unit_price": 999.99,
            "cost_price": 750.00
        }
        
        try:
            response = self.session.post(f"{API_BASE}/products", json=product_data)
            if response.status_code == 200:
                product = response.json()
                self.test_product_id = product['id']
                print_success(f"Product CREATE successful - ID: {self.test_product_id}")
            else:
                print_error(f"Product CREATE failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Product CREATE error: {str(e)}")
            return False
        
        # READ (Single)
        print_info("Testing Product READ (single)...")
        try:
            response = self.session.get(f"{API_BASE}/products/{self.test_product_id}")
            if response.status_code == 200:
                product = response.json()
                if product['item_short_name'] == product_data['item_short_name']:
                    print_success("Product READ (single) successful")
                else:
                    print_error("Product READ data mismatch")
                    return False
            else:
                print_error(f"Product READ failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Product READ error: {str(e)}")
            return False
        
        # READ (List)
        print_info("Testing Product READ (list)...")
        try:
            response = self.session.get(f"{API_BASE}/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list):
                    print_success(f"Product READ (list) successful - Found {len(products)} products")
                else:
                    print_error("Product list format error")
                    return False
            else:
                print_error(f"Product READ (list) failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Product READ (list) error: {str(e)}")
            return False
        
        # UPDATE
        print_info("Testing Product UPDATE...")
        update_data = {
            "item_short_name": "Updated Test Product CRUD",
            "default_unit_price": 1199.99
        }
        try:
            response = self.session.put(f"{API_BASE}/products/{self.test_product_id}", json=update_data)
            if response.status_code == 200:
                updated_product = response.json()
                if updated_product['item_short_name'] == update_data['item_short_name']:
                    print_success("Product UPDATE successful")
                else:
                    print_error("Product UPDATE data mismatch")
                    return False
            else:
                print_error(f"Product UPDATE failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Product UPDATE error: {str(e)}")
            return False
        
        return True
    
    def test_quotation_crud(self):
        """Test Quotation CRUD operations"""
        print_header("Testing Quotation CRUD Operations")
        
        # First create a customer for the quotation
        print_info("Creating customer for quotation test...")
        unique_tax_number = f"{random.randint(1000000000, 9999999999)}"
        customer_data = {
            "name": "Quotation Test Customer Ltd",
            "contact_person": "Bob Smith",
            "email": "bob@quotationtest.com",
            "phone": "+90 212 555 1111",
            "tax_number": unique_tax_number
        }
        
        try:
            response = self.session.post(f"{API_BASE}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                customer_id = customer['id']
                print_success(f"Test customer created for quotation - ID: {customer_id}")
            else:
                print_error("Failed to create customer for quotation test")
                return False
        except Exception as e:
            print_error(f"Error creating customer for quotation: {str(e)}")
            return False
        
        # CREATE Quotation
        print_info("Testing Quotation CREATE...")
        quotation_data = {
            "quotation_type": "sales",
            "customer_id": customer_id,
            "subject": "CRUD Test Quotation",
            "project_code": "CRUD-TEST-001",
            "validity_days": 30,
            "delivery_time": "2-3 weeks",
            "delivery_terms": "EXW Istanbul",
            "payment_terms": "50% advance, 50% on delivery",
            "notes": "This is a CRUD test quotation",
            "language": "english",
            "line_items": [
                {
                    "item_short_name": "Test Item 1",
                    "item_description": "First test item for CRUD",
                    "quantity": 1,
                    "unit": "Pieces",
                    "currency": "EUR",
                    "unit_price": 500.0,
                    "cost_price": 400.0
                },
                {
                    "item_short_name": "Test Item 2",
                    "item_description": "Second test item for CRUD",
                    "quantity": 2,
                    "unit": "Pieces",
                    "currency": "EUR",
                    "unit_price": 300.0,
                    "cost_price": 250.0
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/quotations", json=quotation_data)
            if response.status_code == 200:
                quotation = response.json()
                self.test_quotation_id = quotation['id']
                print_success(f"Quotation CREATE successful - ID: {self.test_quotation_id}")
                print_info(f"Quote No: {quotation['quote_no']}")
            else:
                print_error(f"Quotation CREATE failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Quotation CREATE error: {str(e)}")
            return False
        
        # READ (Single)
        print_info("Testing Quotation READ (single)...")
        try:
            response = self.session.get(f"{API_BASE}/quotations/{self.test_quotation_id}")
            if response.status_code == 200:
                quotation = response.json()
                if quotation['subject'] == quotation_data['subject']:
                    print_success("Quotation READ (single) successful")
                    print_info(f"Retrieved quotation: {quotation['quote_no']}")
                else:
                    print_error("Quotation read data mismatch")
                    return False
            else:
                print_error(f"Quotation read failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Quotation read error: {str(e)}")
            return False
        
        # READ (List)
        print_info("Testing Quotation read (list)...")
        try:
            response = self.session.get(f"{API_BASE}/quotations")
            if response.status_code == 200:
                quotations = response.json()
                if isinstance(quotations, list):
                    print_success(f"Quotation read (list) successful - Found {len(quotations)} quotations")
                else:
                    print_error("Quotation list format error")
                    return False
            else:
                print_error(f"Quotation read (list) failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Quotation read (list) error: {str(e)}")
            return False
        
        # UPDATE
        print_info("Testing Quotation UPDATE...")
        update_data = {
            "subject": "Updated CRUD Test Quotation",
            "notes": "Updated notes for CRUD test"
        }
        try:
            response = self.session.put(f"{API_BASE}/quotations/{self.test_quotation_id}", json=update_data)
            if response.status_code == 200:
                updated_quotation = response.json()
                if updated_quotation['subject'] == update_data['subject']:
                    print_success("Quotation UPDATE successful")
                else:
                    print_error("Quotation UPDATE data mismatch")
                    return False
            else:
                print_error(f"Quotation UPDATE failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Quotation UPDATE error: {str(e)}")
            return False
        
        return True
    
    def test_endpoint_health(self):
        """Test all major API endpoints for basic health"""
        print_header("Testing API Endpoint Health")
        
        endpoints_to_test = [
            ("GET", "/statistics", "Statistics endpoint"),
            ("GET", "/customers", "Customers list endpoint"),
            ("GET", "/products", "Products list endpoint"),
            ("GET", "/quotations", "Quotations list endpoint"),
            ("GET", "/representatives", "Representatives list endpoint"),
            ("GET", "/cost-categories", "Cost categories endpoint"),
            ("GET", "/search", "Search endpoint")
        ]
        
        failed_endpoints = []
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code in [200, 201]:
                    print_success(f"{description}: {response.status_code}")
                else:
                    print_error(f"{description}: {response.status_code}")
                    failed_endpoints.append(f"{method} {endpoint}")
                    
            except Exception as e:
                print_error(f"{description}: Connection error - {str(e)}")
                failed_endpoints.append(f"{method} {endpoint}")
        
        if failed_endpoints:
            print_error(f"Failed endpoints: {', '.join(failed_endpoints)}")
            return False
        else:
            print_success("All endpoint health checks passed")
            return True
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print_header("Testing Error Handling")
        
        # Test 404 errors
        print_info("Testing 404 error handling...")
        try:
            response = self.session.get(f"{API_BASE}/customers/nonexistent-id")
            if response.status_code == 404:
                print_success("404 error handling works correctly")
            else:
                print_warning(f"Expected 404, got {response.status_code}")
        except Exception as e:
            print_error(f"Error testing 404 handling: {str(e)}")
            return False
        
        # Test 400 errors (duplicate tax number)
        print_info("Testing 400 error handling...")
        try:
            # Create a customer first
            customer_data = {
                "name": "Error Test Customer",
                "tax_number": "1234567890"
            }
            response1 = self.session.post(f"{API_BASE}/customers", json=customer_data)
            
            # Try to create another with same tax number
            response2 = self.session.post(f"{API_BASE}/customers", json=customer_data)
            
            if response2.status_code == 400:
                print_success("400 error handling works correctly")
            else:
                print_warning(f"Expected 400 for duplicate tax number, got {response2.status_code}")
        except Exception as e:
            print_error(f"Error testing 400 handling: {str(e)}")
            return False
        
        return True
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print_header("DEMART Comprehensive Backend Testing Suite")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        # Test 1: Database Connection
        test_results.append(("Database Connection", self.test_database_connection()))
        
        # Test 2: Customer CRUD
        test_results.append(("Customer CRUD Operations", self.test_customer_crud()))
        
        # Test 3: Product CRUD
        test_results.append(("Product CRUD Operations", self.test_product_crud()))
        
        # Test 4: Quotation CRUD
        test_results.append(("Quotation CRUD Operations", self.test_quotation_crud()))
        
        # Test 5: Endpoint Health
        test_results.append(("API Endpoint Health", self.test_endpoint_health()))
        
        # Test 6: Error Handling
        test_results.append(("Error Handling", self.test_error_handling()))
        
        # Print Summary
        self.print_test_summary(test_results)
        
        return all(result for _, result in test_results)
    
    def print_test_summary(self, test_results):
        """Print test summary"""
        print_header("COMPREHENSIVE TEST SUMMARY")
        
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
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL COMPREHENSIVE TESTS PASSED! 🎉{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}✅ SYSTEM IS READY FOR DEPLOYMENT ✅{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED ❌{Colors.ENDC}")
            print(f"{Colors.RED}{Colors.BOLD}⚠️  DEPLOYMENT NOT RECOMMENDED ⚠️{Colors.ENDC}")

def main():
    """Main function"""
    tester = ComprehensiveTester()
    success = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()