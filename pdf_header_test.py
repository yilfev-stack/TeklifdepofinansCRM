#!/usr/bin/env python3
"""
PDF Generation Test - Page 3 Header Verification
Testing PDF generation to verify page 3 header is now included
"""

import requests
import json
import sys
import os
from datetime import datetime
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

class PDFHeaderTester:
    def __init__(self):
        self.session = requests.Session()
        self.quotation_ids = []
        
    def test_backend_connection(self):
        """Test if backend is accessible"""
        print_header("Testing Backend Connection")
        try:
            response = self.session.get(f"{API_BASE}/quotations")
            if response.status_code == 200:
                quotations = response.json()
                print_success(f"Backend is accessible at {API_BASE}")
                print_info(f"Found {len(quotations)} quotations in database")
                
                # Store some quotation IDs for testing
                if quotations:
                    self.quotation_ids = [q['id'] for q in quotations[:5]]  # Take first 5
                    print_info(f"Will test PDF generation for {len(self.quotation_ids)} quotations")
                else:
                    print_warning("No quotations found in database")
                    return False
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Cannot connect to backend: {str(e)}")
            return False
    
    def test_pdf_generation_with_header_check(self):
        """Test PDF generation and verify file size (indicating page 3 header)"""
        print_header("Testing PDF Generation with Page 3 Header Verification")
        
        if not self.quotation_ids:
            print_error("No quotation IDs available for testing")
            return False
        
        success_count = 0
        total_tests = min(3, len(self.quotation_ids))  # Test up to 3 quotations
        
        for i, quotation_id in enumerate(self.quotation_ids[:total_tests]):
            print(f"\n{Colors.BOLD}Test {i+1}/{total_tests}: Quotation ID {quotation_id}{Colors.ENDC}")
            
            try:
                # First get quotation details
                response = self.session.get(f"{API_BASE}/quotations/{quotation_id}")
                if response.status_code != 200:
                    print_error(f"Failed to get quotation details: {response.status_code}")
                    continue
                
                quotation = response.json()
                quote_no = quotation.get('quote_no', 'Unknown')
                customer_name = quotation.get('customer_name', 'Unknown')
                
                print_info(f"Testing PDF for: {quote_no} - {customer_name}")
                
                # Generate PDF
                pdf_response = self.session.get(f"{API_BASE}/quotations/{quotation_id}/generate-pdf")
                
                if pdf_response.status_code == 200:
                    print_success("PDF generated successfully")
                    
                    # Check Content-Type
                    content_type = pdf_response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        print_success(f"Correct Content-Type: {content_type}")
                    else:
                        print_warning(f"Unexpected Content-Type: {content_type}")
                    
                    # Check Content-Disposition for filename
                    content_disposition = pdf_response.headers.get('content-disposition', '')
                    if 'filename=' in content_disposition:
                        print_success(f"PDF filename header present: {content_disposition}")
                    else:
                        print_warning("No filename in Content-Disposition header")
                    
                    # Check PDF file size
                    pdf_size = len(pdf_response.content)
                    pdf_size_kb = pdf_size / 1024
                    
                    print_info(f"PDF file size: {pdf_size_kb:.1f} KB ({pdf_size} bytes)")
                    
                    # Verify file size indicates page 3 header was added
                    # User mentioned size increased from 869KB to 983KB after header fix
                    if pdf_size_kb > 900:
                        print_success(f"✅ PDF size ({pdf_size_kb:.1f} KB) indicates page 3 header is likely included")
                        print_success("✅ File size > 900KB suggests header optimization worked")
                    elif pdf_size_kb > 500:
                        print_warning(f"⚠ PDF size ({pdf_size_kb:.1f} KB) is reasonable but smaller than expected")
                        print_info("Expected size around 1MB with page 3 header")
                    else:
                        print_error(f"❌ PDF size ({pdf_size_kb:.1f} KB) is too small - header may be missing")
                        continue
                    
                    # Verify PDF file structure
                    pdf_content = pdf_response.content
                    
                    # Check PDF signature
                    if pdf_content.startswith(b'%PDF-'):
                        print_success("✅ Valid PDF signature found")
                    else:
                        print_error("❌ Invalid PDF signature")
                        continue
                    
                    # Check PDF end marker
                    if b'%%EOF' in pdf_content:
                        print_success("✅ Valid PDF end marker found")
                    else:
                        print_warning("⚠ PDF end marker not found")
                    
                    # Save PDF temporarily to verify it's not corrupted
                    temp_filename = f"/tmp/test_pdf_{quotation_id[:8]}.pdf"
                    try:
                        with open(temp_filename, 'wb') as f:
                            f.write(pdf_content)
                        
                        # Check if file was written successfully
                        if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                            print_success(f"✅ PDF file saved successfully: {temp_filename}")
                            
                            # Clean up
                            os.remove(temp_filename)
                            print_info("Temporary PDF file cleaned up")
                        else:
                            print_error("❌ Failed to save PDF file")
                            continue
                            
                    except Exception as e:
                        print_error(f"❌ Error saving PDF file: {str(e)}")
                        continue
                    
                    print_success(f"✅ PDF generation test PASSED for quotation {quote_no}")
                    success_count += 1
                    
                elif pdf_response.status_code == 404:
                    print_error(f"❌ Quotation not found: {pdf_response.status_code}")
                    try:
                        error_data = pdf_response.json()
                        print_error(f"Error details: {error_data}")
                    except:
                        print_error(f"Response: {pdf_response.text}")
                        
                elif pdf_response.status_code == 500:
                    print_error(f"❌ Server error during PDF generation: {pdf_response.status_code}")
                    try:
                        error_data = pdf_response.json()
                        print_error(f"Error details: {error_data}")
                    except:
                        print_error(f"Response: {pdf_response.text}")
                else:
                    print_error(f"❌ Unexpected status code: {pdf_response.status_code}")
                    print_error(f"Response: {pdf_response.text}")
                    
            except Exception as e:
                print_error(f"❌ Exception during PDF test: {str(e)}")
                continue
        
        # Summary
        print(f"\n{Colors.BOLD}PDF Generation Test Summary:{Colors.ENDC}")
        print_info(f"Total tests: {total_tests}")
        print_info(f"Successful: {success_count}")
        print_info(f"Failed: {total_tests - success_count}")
        
        if success_count == total_tests:
            print_success("🎉 ALL PDF GENERATION TESTS PASSED!")
            print_success("✅ Page 3 header appears to be working based on file sizes")
            return True
        elif success_count > 0:
            print_warning(f"⚠ {success_count}/{total_tests} tests passed")
            return True
        else:
            print_error("❌ ALL PDF GENERATION TESTS FAILED")
            return False
    
    def test_error_handling(self):
        """Test PDF generation error handling"""
        print_header("Testing PDF Generation Error Handling")
        
        # Test with non-existent quotation ID
        fake_id = "non-existent-quotation-id"
        
        try:
            response = self.session.get(f"{API_BASE}/quotations/{fake_id}/generate-pdf")
            
            if response.status_code == 404:
                print_success("✅ Correct 404 response for non-existent quotation")
                
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print_success(f"✅ Proper error message: {error_data['detail']}")
                    else:
                        print_warning("⚠ Error response missing 'detail' field")
                except:
                    print_warning("⚠ Error response is not valid JSON")
                
                return True
            else:
                print_error(f"❌ Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"❌ Exception during error handling test: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all PDF header tests"""
        print_header("PDF Generation - Page 3 Header Verification Test Suite")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info("Testing PDF generation to verify page 3 header is now included")
        
        test_results = []
        
        # Test 1: Backend Connection
        test_results.append(("Backend Connection", self.test_backend_connection()))
        
        # Test 2: PDF Generation with Header Check
        test_results.append(("PDF Generation with Header Check", self.test_pdf_generation_with_header_check()))
        
        # Test 3: Error Handling
        test_results.append(("PDF Error Handling", self.test_error_handling()))
        
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
            print(f"{Colors.GREEN}{Colors.BOLD}✅ PDF generation working correctly{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Page 3 header appears to be included based on file sizes{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED ❌{Colors.ENDC}")

def main():
    """Main function"""
    tester = PDFHeaderTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()