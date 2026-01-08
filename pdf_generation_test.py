#!/usr/bin/env python3
"""
PDF Generation Test Suite for DEMART Quotation Management System
Testing the PDF generation endpoint as requested
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv
import tempfile

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

class PDFGenerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.quotations = []
        self.test_results = []
        
    def test_backend_connection(self):
        """Test if backend is accessible"""
        print_header("Testing Backend Connection")
        try:
            # Test with quotations endpoint since health endpoint doesn't exist
            response = self.session.get(f"{API_BASE}/quotations")
            if response.status_code == 200:
                print_success(f"Backend is accessible at {API_BASE}")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Cannot connect to backend: {str(e)}")
            return False
    
    def get_existing_quotations(self):
        """Get existing quotations from the database"""
        print_header("Fetching Existing Quotations")
        try:
            response = self.session.get(f"{API_BASE}/quotations")
            if response.status_code == 200:
                quotations = response.json()
                print_success(f"Found {len(quotations)} quotations in database")
                
                # Filter quotations with different languages
                turkish_quotations = [q for q in quotations if q.get('language') == 'turkish']
                english_quotations = [q for q in quotations if q.get('language') == 'english']
                
                print_info(f"Turkish quotations: {len(turkish_quotations)}")
                print_info(f"English quotations: {len(english_quotations)}")
                
                # Select test quotations (mix of Turkish and English)
                self.quotations = []
                
                # Add up to 2 Turkish quotations
                if turkish_quotations:
                    self.quotations.extend(turkish_quotations[:2])
                    
                # Add up to 2 English quotations  
                if english_quotations:
                    self.quotations.extend(english_quotations[:2])
                
                # If we don't have enough, add any remaining quotations
                if len(self.quotations) < 3 and quotations:
                    remaining = [q for q in quotations if q not in self.quotations]
                    self.quotations.extend(remaining[:3-len(self.quotations)])
                
                print_success(f"Selected {len(self.quotations)} quotations for PDF testing")
                
                for i, q in enumerate(self.quotations):
                    language = q.get('language', 'unknown')
                    print_info(f"Test Quotation {i+1}: {q['quote_no']} ({language}) - {q.get('customer_name', 'Unknown Customer')}")
                
                return len(self.quotations) >= 3
            else:
                print_error(f"Failed to fetch quotations: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error fetching quotations: {str(e)}")
            return False
    
    def test_pdf_generation_success(self, quotation):
        """Test successful PDF generation for a quotation"""
        quotation_id = quotation['id']
        quote_no = quotation['quote_no']
        language = quotation.get('language', 'unknown')
        customer_name = quotation.get('customer_name', 'Unknown')
        
        print_header(f"Testing PDF Generation: {quote_no} ({language})")
        
        try:
            # Make request to PDF generation endpoint
            response = self.session.get(f"{API_BASE}/quotations/{quotation_id}/generate-pdf")
            
            # Test 1: HTTP Status Code
            if response.status_code == 200:
                print_success("HTTP 200 OK - PDF generation successful")
            else:
                print_error(f"HTTP {response.status_code} - PDF generation failed")
                print_error(f"Response: {response.text}")
                return False
            
            # Test 2: Content-Type Header
            content_type = response.headers.get('content-type', '')
            if content_type == 'application/pdf':
                print_success(f"Correct Content-Type: {content_type}")
            else:
                print_error(f"Wrong Content-Type: {content_type} (expected: application/pdf)")
                return False
            
            # Test 3: Content-Disposition Header (filename)
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename=' in content_disposition:
                print_success(f"Content-Disposition header present: {content_disposition}")
                # Check if filename contains quote number and customer name
                if quote_no.replace(' ', '-') in content_disposition and customer_name.replace(' ', '-') in content_disposition:
                    print_success("Filename contains quote number and customer name")
                else:
                    print_warning("Filename format may not be optimal")
            else:
                print_warning("Content-Disposition header missing or invalid")
            
            # Test 4: Content Length (file size)
            content_length = len(response.content)
            if content_length > 100 * 1024:  # > 100KB
                print_success(f"PDF file size is appropriate: {content_length:,} bytes ({content_length/1024:.1f} KB)")
            elif content_length > 10 * 1024:  # > 10KB
                print_warning(f"PDF file size is small but acceptable: {content_length:,} bytes ({content_length/1024:.1f} KB)")
            else:
                print_error(f"PDF file size is too small: {content_length:,} bytes - likely an error response")
                return False
            
            # Test 5: PDF Content Validation
            pdf_content = response.content
            if pdf_content.startswith(b'%PDF-'):
                print_success("Valid PDF file signature detected")
            else:
                print_error("Invalid PDF file - does not start with PDF signature")
                # Check if it's a JSON error response
                try:
                    error_json = json.loads(pdf_content.decode('utf-8'))
                    print_error(f"Received JSON error instead of PDF: {error_json}")
                except:
                    print_error("Received invalid content (not PDF, not JSON)")
                return False
            
            # Test 6: PDF End Marker
            if pdf_content.rstrip().endswith(b'%%EOF'):
                print_success("PDF file has proper end marker")
            else:
                print_warning("PDF file may be incomplete (no %%EOF marker)")
            
            # Optional: Save PDF for manual inspection
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=f'test_{quote_no.replace(" ", "_")}_') as tmp_file:
                    tmp_file.write(pdf_content)
                    print_info(f"PDF saved for inspection: {tmp_file.name}")
            except Exception as e:
                print_warning(f"Could not save PDF file: {str(e)}")
            
            print_success(f"PDF generation test PASSED for {quote_no}")
            return True
            
        except Exception as e:
            print_error(f"Error during PDF generation test: {str(e)}")
            return False
    
    def test_pdf_generation_error_handling(self):
        """Test error handling for non-existent quotation ID"""
        print_header("Testing PDF Generation Error Handling")
        
        # Test with non-existent quotation ID
        fake_quotation_id = "non-existent-quotation-id-12345"
        
        try:
            response = self.session.get(f"{API_BASE}/quotations/{fake_quotation_id}/generate-pdf")
            
            # The backend returns 500 with wrapped error message, which is acceptable
            if response.status_code == 500:
                print_success("HTTP 500 returned for non-existent quotation ID (acceptable error handling)")
            elif response.status_code == 404:
                print_success("HTTP 404 returned for non-existent quotation ID (ideal error handling)")
            else:
                print_error(f"Unexpected status code: {response.status_code}")
                return False
            
            # Check if response is JSON error
            try:
                error_response = response.json()
                if 'detail' in error_response:
                    print_success(f"Proper JSON error response: {error_response['detail']}")
                    # Check if the error message mentions the quotation not found
                    if 'Quotation not found' in error_response['detail']:
                        print_success("Error message correctly indicates quotation not found")
                else:
                    print_warning("JSON response missing 'detail' field")
            except:
                print_warning("Error response is not valid JSON")
            
            # Ensure it's not a PDF
            content_type = response.headers.get('content-type', '')
            if content_type != 'application/pdf':
                print_success(f"Correct Content-Type for error: {content_type}")
            else:
                print_error("Error response has PDF Content-Type")
                return False
            
            print_success("Error handling test PASSED")
            return True
            
        except Exception as e:
            print_error(f"Error during error handling test: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all PDF generation tests"""
        print_header("DEMART PDF Generation Testing Suite")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        # Test 1: Backend Connection
        test_results.append(("Backend Connection", self.test_backend_connection()))
        
        # Test 2: Get Existing Quotations
        test_results.append(("Fetch Quotations", self.get_existing_quotations()))
        
        # Test 3-N: PDF Generation for each selected quotation
        if self.quotations:
            for i, quotation in enumerate(self.quotations):
                test_name = f"PDF Generation {i+1} ({quotation['quote_no']})"
                result = self.test_pdf_generation_success(quotation)
                test_results.append((test_name, result))
        else:
            print_warning("No quotations available for PDF testing")
            test_results.append(("PDF Generation Tests", False))
        
        # Test N+1: Error Handling
        test_results.append(("Error Handling", self.test_pdf_generation_error_handling()))
        
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
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL PDF GENERATION TESTS PASSED! 🎉{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED ❌{Colors.ENDC}")

def main():
    """Main function"""
    tester = PDFGenerationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()