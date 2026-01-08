#!/usr/bin/env python3
"""
Backend Test Suite for DEMART Quotation Management System
Testing the revision functionality as requested
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

class RevisionTester:
    def __init__(self):
        self.session = requests.Session()
        self.customer_id = None
        self.quotation_id = None
        self.revision_ids = []
        self.base_quote_no = None
        self.revision_group_id = None
        
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
    
    def create_test_customer(self):
        """Create a test customer for quotations"""
        print_header("Creating Test Customer")
        
        import random
        unique_tax_number = f"{random.randint(1000000000, 9999999999)}"
        
        customer_data = {
            "name": "Acme Corporation Ltd",
            "contact_person": "John Smith",
            "email": "john.smith@acme.com",
            "phone": "+90 212 555 0123",
            "address": "Maslak Mahallesi, Büyükdere Caddesi No:123",
            "city": "Istanbul",
            "country": "Turkey",
            "tax_office": "Maslak Vergi Dairesi",
            "tax_number": unique_tax_number
        }
        
        try:
            response = self.session.post(f"{API_BASE}/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                self.customer_id = customer['id']
                print_success(f"Customer created with ID: {self.customer_id}")
                print_info(f"Customer name: {customer['name']}")
                return True
            else:
                print_error(f"Failed to create customer: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Error creating customer: {str(e)}")
            return False
    
    def create_initial_quotation(self):
        """Create the initial quotation (Step 1)"""
        print_header("Step 1: Creating Initial Quotation")
        
        quotation_data = {
            "quotation_type": "sales",
            "customer_id": self.customer_id,
            "subject": "Industrial Equipment Supply - Revision Test",
            "project_code": "PRJ-2025-001",
            "validity_days": 30,
            "delivery_time": "4-6 weeks",
            "delivery_terms": "EXW Istanbul",
            "payment_terms": "30% advance, 70% before shipment",
            "notes": "This is a test quotation for revision functionality",
            "language": "english",
            "line_items": [
                {
                    "item_short_name": "Industrial Pump Model X1",
                    "item_description": "High-pressure industrial pump with stainless steel construction",
                    "quantity": 2,
                    "unit": "Pieces",
                    "currency": "EUR",
                    "unit_price": 1500.0,
                    "cost_price": 1200.0
                },
                {
                    "item_short_name": "Control Panel CP-100",
                    "item_description": "Digital control panel with touch screen interface",
                    "quantity": 1,
                    "unit": "Pieces", 
                    "currency": "EUR",
                    "unit_price": 800.0,
                    "cost_price": 600.0
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/quotations", json=quotation_data)
            if response.status_code == 200:
                quotation = response.json()
                self.quotation_id = quotation['id']
                self.base_quote_no = quotation['base_quote_no']
                self.revision_group_id = quotation['revision_group_id']
                
                print_success(f"Initial quotation created successfully")
                print_info(f"Quotation ID: {self.quotation_id}")
                print_info(f"Quote No: {quotation['quote_no']}")
                print_info(f"Base Quote No: {self.base_quote_no}")
                print_info(f"Revision No: {quotation['revision_no']}")
                print_info(f"Revision Group ID: {self.revision_group_id}")
                
                # Validate initial quotation structure
                self.validate_quotation_structure(quotation, 0)
                return True
            else:
                print_error(f"Failed to create quotation: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Error creating quotation: {str(e)}")
            return False
    
    def create_first_revision(self):
        """Create the first revision (Step 2)"""
        print_header("Step 2: Creating First Revision")
        
        try:
            response = self.session.post(f"{API_BASE}/quotations/{self.quotation_id}/revise")
            if response.status_code == 200:
                revision = response.json()
                revision_id = revision['id']
                self.revision_ids.append(revision_id)
                
                print_success(f"First revision created successfully")
                print_info(f"Revision ID: {revision_id}")
                print_info(f"Quote No: {revision['quote_no']}")
                print_info(f"Base Quote No: {revision['base_quote_no']}")
                print_info(f"Revision No: {revision['revision_no']}")
                print_info(f"Revision Group ID: {revision['revision_group_id']}")
                
                # Validate revision structure
                self.validate_quotation_structure(revision, 1)
                return True
            else:
                print_error(f"Failed to create first revision: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Error creating first revision: {str(e)}")
            return False
    
    def get_revision_history_first_check(self):
        """Get revision history after first revision (Step 3)"""
        print_header("Step 3: Getting Revision History (After First Revision)")
        
        try:
            response = self.session.get(f"{API_BASE}/quotations/{self.quotation_id}/revisions")
            if response.status_code == 200:
                revisions = response.json()
                
                print_success(f"Retrieved revision history successfully")
                print_info(f"Total revisions found: {len(revisions)}")
                
                # Should have 2 revisions now (original + first revision)
                if len(revisions) == 2:
                    print_success("Correct number of revisions (2)")
                else:
                    print_error(f"Expected 2 revisions, found {len(revisions)}")
                    return False
                
                # Validate each revision
                for i, revision in enumerate(revisions):
                    print_info(f"Revision {i}: {revision['quote_no']} (Rev No: {revision['revision_no']})")
                    self.validate_quotation_structure(revision, revision['revision_no'])
                
                return True
            else:
                print_error(f"Failed to get revision history: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Error getting revision history: {str(e)}")
            return False
    
    def create_second_revision(self):
        """Create the second revision (Step 4)"""
        print_header("Step 4: Creating Second Revision")
        
        try:
            response = self.session.post(f"{API_BASE}/quotations/{self.quotation_id}/revise")
            if response.status_code == 200:
                revision = response.json()
                revision_id = revision['id']
                self.revision_ids.append(revision_id)
                
                print_success(f"Second revision created successfully")
                print_info(f"Revision ID: {revision_id}")
                print_info(f"Quote No: {revision['quote_no']}")
                print_info(f"Base Quote No: {revision['base_quote_no']}")
                print_info(f"Revision No: {revision['revision_no']}")
                print_info(f"Revision Group ID: {revision['revision_group_id']}")
                
                # Validate revision structure
                self.validate_quotation_structure(revision, 2)
                return True
            else:
                print_error(f"Failed to create second revision: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Error creating second revision: {str(e)}")
            return False
    
    def get_final_revision_history(self):
        """Get final revision history (Step 5)"""
        print_header("Step 5: Getting Final Revision History")
        
        try:
            response = self.session.get(f"{API_BASE}/quotations/{self.quotation_id}/revisions")
            if response.status_code == 200:
                revisions = response.json()
                
                print_success(f"Retrieved final revision history successfully")
                print_info(f"Total revisions found: {len(revisions)}")
                
                # Should have 3 revisions now (original + 2 revisions)
                if len(revisions) == 3:
                    print_success("Correct number of revisions (3)")
                else:
                    print_error(f"Expected 3 revisions, found {len(revisions)}")
                    return False
                
                # Validate each revision and check ordering
                expected_revision_nos = [0, 1, 2]
                for i, revision in enumerate(revisions):
                    expected_rev_no = expected_revision_nos[i]
                    actual_rev_no = revision['revision_no']
                    
                    print_info(f"Revision {i}: {revision['quote_no']} (Rev No: {actual_rev_no})")
                    
                    if actual_rev_no == expected_rev_no:
                        print_success(f"Revision {i} has correct revision number: {actual_rev_no}")
                    else:
                        print_error(f"Revision {i} has wrong revision number. Expected: {expected_rev_no}, Got: {actual_rev_no}")
                        return False
                    
                    self.validate_quotation_structure(revision, actual_rev_no)
                
                return True
            else:
                print_error(f"Failed to get final revision history: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Error getting final revision history: {str(e)}")
            return False
    
    def validate_quotation_structure(self, quotation, expected_revision_no):
        """Validate quotation structure and revision fields"""
        print_info(f"Validating quotation structure for revision {expected_revision_no}")
        
        # Check revision number
        if quotation['revision_no'] == expected_revision_no:
            print_success(f"Revision number is correct: {expected_revision_no}")
        else:
            print_error(f"Wrong revision number. Expected: {expected_revision_no}, Got: {quotation['revision_no']}")
        
        # Check base_quote_no consistency
        if self.base_quote_no and quotation['base_quote_no'] == self.base_quote_no:
            print_success(f"Base quote number is consistent: {self.base_quote_no}")
        else:
            if self.base_quote_no:
                print_error(f"Base quote number mismatch. Expected: {self.base_quote_no}, Got: {quotation['base_quote_no']}")
            else:
                print_info(f"Base quote number: {quotation['base_quote_no']}")
        
        # Check quote_no format
        expected_quote_no = self.base_quote_no if expected_revision_no == 0 else f"{self.base_quote_no} Rev {expected_revision_no}"
        if quotation['quote_no'] == expected_quote_no:
            print_success(f"Quote number format is correct: {quotation['quote_no']}")
        else:
            print_error(f"Wrong quote number format. Expected: {expected_quote_no}, Got: {quotation['quote_no']}")
        
        # Check revision_group_id consistency
        if self.revision_group_id and quotation['revision_group_id'] == self.revision_group_id:
            print_success(f"Revision group ID is consistent: {self.revision_group_id}")
        else:
            if self.revision_group_id:
                print_error(f"Revision group ID mismatch. Expected: {self.revision_group_id}, Got: {quotation['revision_group_id']}")
            else:
                print_info(f"Revision group ID: {quotation['revision_group_id']}")
        
        # Check required fields
        required_fields = ['id', 'quotation_type', 'customer_id', 'subject']
        for field in required_fields:
            if field in quotation and quotation[field]:
                print_success(f"Required field '{field}' is present")
            else:
                print_error(f"Required field '{field}' is missing or empty")
        
        # Check line items
        if 'line_items' in quotation and quotation['line_items']:
            print_success(f"Line items are present ({len(quotation['line_items'])} items)")
            for i, item in enumerate(quotation['line_items']):
                if 'id' in item and item['id']:
                    print_success(f"Line item {i+1} has unique ID: {item['id']}")
                else:
                    print_error(f"Line item {i+1} is missing ID")
        else:
            print_warning("No line items found")
    
    def test_revision_from_revision(self):
        """Test creating a revision from a revision (not original)"""
        print_header("Additional Test: Creating Revision from Revision")
        
        if not self.revision_ids:
            print_warning("No revisions available for this test")
            return True
        
        # Use the first revision ID to create another revision
        first_revision_id = self.revision_ids[0]
        
        try:
            response = self.session.post(f"{API_BASE}/quotations/{first_revision_id}/revise")
            if response.status_code == 200:
                revision = response.json()
                
                print_success(f"Revision from revision created successfully")
                print_info(f"New Revision ID: {revision['id']}")
                print_info(f"Quote No: {revision['quote_no']}")
                print_info(f"Revision No: {revision['revision_no']}")
                
                # This should be revision 3 (0, 1, 2, 3)
                if revision['revision_no'] == 3:
                    print_success("Revision number incremented correctly from revision")
                else:
                    print_error(f"Expected revision number 3, got {revision['revision_no']}")
                
                # Check that it still belongs to the same revision group
                if revision['revision_group_id'] == self.revision_group_id:
                    print_success("Revision group ID maintained correctly")
                else:
                    print_error("Revision group ID changed unexpectedly")
                
                return True
            else:
                print_error(f"Failed to create revision from revision: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error creating revision from revision: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print_header("Cleaning Up Test Data")
        
        # Note: In a real scenario, you might want to delete test data
        # For now, we'll just mark the customer as inactive
        if self.customer_id:
            try:
                response = self.session.delete(f"{API_BASE}/customers/{self.customer_id}")
                if response.status_code == 200:
                    print_success("Test customer deactivated")
                else:
                    print_warning(f"Could not deactivate test customer: {response.status_code}")
            except Exception as e:
                print_warning(f"Error during cleanup: {str(e)}")
    
    def run_all_tests(self):
        """Run all revision tests"""
        print_header("DEMART Quotation Revision Testing Suite")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        # Test 1: Backend Connection
        test_results.append(("Backend Connection", self.test_backend_connection()))
        
        # Test 2: Create Test Customer
        test_results.append(("Create Test Customer", self.create_test_customer()))
        
        # Test 3: Create Initial Quotation
        test_results.append(("Create Initial Quotation", self.create_initial_quotation()))
        
        # Test 4: Create First Revision
        test_results.append(("Create First Revision", self.create_first_revision()))
        
        # Test 5: Get Revision History (First Check)
        test_results.append(("Get Revision History (First)", self.get_revision_history_first_check()))
        
        # Test 6: Create Second Revision
        test_results.append(("Create Second Revision", self.create_second_revision()))
        
        # Test 7: Get Final Revision History
        test_results.append(("Get Final Revision History", self.get_final_revision_history()))
        
        # Test 8: Test Revision from Revision
        test_results.append(("Revision from Revision", self.test_revision_from_revision()))
        
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
    tester = RevisionTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()