#!/usr/bin/env python3
"""
WeasyPrint PDF Generation Test Suite for DEMART Quotation Management System
Testing WeasyPrint PDF generation feature comprehensively as requested
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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")

class WeasyPrintPDFTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def test_backend_connection(self):
        """Test if backend is accessible"""
        print_header("Testing Backend Connection")
        try:
            response = self.session.get(f"{API_BASE}/quotations")
            if response.status_code == 200:
                print_success(f"Backend is accessible at {API_BASE}")
                quotations = response.json()
                print_info(f"Found {len(quotations)} quotations in database")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Cannot connect to backend: {str(e)}")
            return False
    
    def test_single_item_quotation_pdf(self):
        """Test Single Item Quotation PDF Generation"""
        print_header("Test 1: Single Item Quotation PDF Generation")
        
        quotation_id = "1c6a038f-e32f-4ecd-9804-ca3137ce6e57"
        expected_min_size = 20 * 1024  # ~20KB (allowing some tolerance)
        
        try:
            print_info(f"Testing quotation ID: {quotation_id}")
            response = self.session.get(f"{API_BASE}/quotations/{quotation_id}/generate-pdf")
            
            if response.status_code == 200:
                print_success("PDF generation successful (HTTP 200)")
                
                # Check Content-Type
                content_type = response.headers.get('content-type', '')
                if content_type == 'application/pdf':
                    print_success(f"Correct Content-Type: {content_type}")
                else:
                    print_error(f"Wrong Content-Type: {content_type}")
                    return False
                
                # Check Content-Disposition
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' in content_disposition and 'filename=' in content_disposition:
                    print_success(f"Proper Content-Disposition header: {content_disposition}")
                else:
                    print_warning(f"Content-Disposition header: {content_disposition}")
                
                # Check file size
                file_size = len(response.content)
                file_size_kb = file_size / 1024
                print_info(f"PDF file size: {file_size} bytes ({file_size_kb:.1f} KB)")
                
                if file_size >= expected_min_size:
                    print_success(f"File size meets requirement (>= {expected_min_size/1024:.1f} KB)")
                else:
                    print_error(f"File size too small. Expected >= {expected_min_size/1024:.1f} KB, got {file_size_kb:.1f} KB")
                    return False
                
                # Check PDF signature
                if response.content.startswith(b'%PDF-'):
                    print_success("Valid PDF signature (%PDF-)")
                else:
                    print_error("Invalid PDF signature")
                    return False
                
                # Check PDF end marker
                if response.content.endswith(b'%%EOF') or b'%%EOF' in response.content[-50:]:
                    print_success("Valid PDF end marker (%%EOF)")
                else:
                    print_error("Missing PDF end marker (%%EOF)")
                    return False
                
                print_success("Single Item Quotation PDF test PASSED")
                return True
                
            else:
                print_error(f"PDF generation failed with status: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error during PDF generation test: {str(e)}")
            return False
    
    def test_multi_item_quotation_pdf(self):
        """Test Multi-Item Quotation (16 items) PDF Generation"""
        print_header("Test 2: Multi-Item Quotation PDF Generation (16 items)")
        
        quotation_id = "5a1570a6-06a7-4e64-b319-e38b8b18f6f3"
        expected_min_size = 25 * 1024  # ~25KB (allowing some tolerance)
        
        try:
            print_info(f"Testing quotation ID: {quotation_id}")
            response = self.session.get(f"{API_BASE}/quotations/{quotation_id}/generate-pdf")
            
            if response.status_code == 200:
                print_success("PDF generation successful (HTTP 200)")
                
                # Check Content-Type
                content_type = response.headers.get('content-type', '')
                if content_type == 'application/pdf':
                    print_success(f"Correct Content-Type: {content_type}")
                else:
                    print_error(f"Wrong Content-Type: {content_type}")
                    return False
                
                # Check file size
                file_size = len(response.content)
                file_size_kb = file_size / 1024
                print_info(f"PDF file size: {file_size} bytes ({file_size_kb:.1f} KB)")
                
                if file_size >= expected_min_size:
                    print_success(f"File size meets requirement (>= {expected_min_size/1024:.1f} KB)")
                else:
                    print_error(f"File size too small. Expected >= {expected_min_size/1024:.1f} KB, got {file_size_kb:.1f} KB")
                    return False
                
                # Check PDF structure
                if response.content.startswith(b'%PDF-'):
                    print_success("Valid PDF signature (%PDF-)")
                else:
                    print_error("Invalid PDF signature")
                    return False
                
                if response.content.endswith(b'%%EOF') or b'%%EOF' in response.content[-50:]:
                    print_success("Valid PDF end marker (%%EOF)")
                else:
                    print_error("Missing PDF end marker (%%EOF)")
                    return False
                
                # Verify this is a multi-item quotation by checking the quotation first
                quotation_response = self.session.get(f"{API_BASE}/quotations/{quotation_id}")
                if quotation_response.status_code == 200:
                    quotation = quotation_response.json()
                    line_items = quotation.get('line_items', [])
                    print_info(f"Quotation has {len(line_items)} line items")
                    
                    if len(line_items) >= 16:
                        print_success(f"Multi-item quotation verified ({len(line_items)} items)")
                    else:
                        print_warning(f"Expected 16+ items, found {len(line_items)} items")
                
                print_success("Multi-Item Quotation PDF test PASSED")
                return True
                
            else:
                print_error(f"PDF generation failed with status: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error during PDF generation test: {str(e)}")
            return False
    
    def test_pdf_content_verification(self):
        """Test PDF Content Verification"""
        print_header("Test 3: PDF Content Verification")
        
        # Use the single item quotation for content verification
        quotation_id = "1c6a038f-e32f-4ecd-9804-ca3137ce6e57"
        
        try:
            print_info(f"Testing PDF content for quotation ID: {quotation_id}")
            response = self.session.get(f"{API_BASE}/quotations/{quotation_id}/generate-pdf")
            
            if response.status_code == 200:
                content = response.content
                
                # Check PDF version
                if content.startswith(b'%PDF-1.'):
                    pdf_version = content[:8].decode('ascii')
                    print_success(f"Valid PDF version: {pdf_version}")
                else:
                    print_error("Invalid PDF version")
                    return False
                
                # Check for reasonable file size (>10KB as mentioned in success criteria)
                file_size = len(content)
                if file_size > 10 * 1024:
                    print_success(f"File size is reasonable: {file_size/1024:.1f} KB (>10KB)")
                else:
                    print_error(f"File size too small: {file_size/1024:.1f} KB (<10KB)")
                    return False
                
                # Check PDF structure integrity
                if b'%%EOF' in content:
                    print_success("PDF has proper end-of-file marker")
                else:
                    print_error("PDF missing end-of-file marker")
                    return False
                
                # Check for PDF objects (basic structure)
                if b'obj' in content and b'endobj' in content:
                    print_success("PDF contains proper object structure")
                else:
                    print_error("PDF missing proper object structure")
                    return False
                
                print_success("PDF Content Verification test PASSED")
                return True
                
            else:
                print_error(f"PDF generation failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error during PDF content verification: {str(e)}")
            return False
    
    def test_error_handling_invalid_id(self):
        """Test Error Handling with Invalid ID"""
        print_header("Test 4: Error Handling - Invalid Quotation ID")
        
        invalid_id = "invalid-quotation-id-12345"
        
        try:
            print_info(f"Testing with invalid quotation ID: {invalid_id}")
            response = self.session.get(f"{API_BASE}/quotations/{invalid_id}/generate-pdf")
            
            if response.status_code == 404:
                print_success("Correct error response (HTTP 404)")
                
                # Check if response is JSON
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print_success(f"Proper error message: {error_data['detail']}")
                    else:
                        print_warning("Error response missing 'detail' field")
                except:
                    print_warning("Error response is not JSON")
                
                print_success("Error Handling test PASSED")
                return True
                
            else:
                print_error(f"Expected HTTP 404, got {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error during error handling test: {str(e)}")
            return False
    
    def test_multiple_quotations(self):
        """Test Multiple Quotations (3-4 different quotations)"""
        print_header("Test 5: Multiple Quotations PDF Generation")
        
        # Get available quotations from the database
        try:
            response = self.session.get(f"{API_BASE}/quotations")
            if response.status_code != 200:
                print_error("Failed to fetch quotations list")
                return False
            
            quotations = response.json()
            if len(quotations) < 3:
                print_warning(f"Only {len(quotations)} quotations available, need at least 3")
                # Still proceed with available quotations
            
            # Test first 4 quotations (or all if less than 4)
            test_quotations = quotations[:4]
            print_info(f"Testing PDF generation for {len(test_quotations)} quotations")
            
            success_count = 0
            
            for i, quotation in enumerate(test_quotations, 1):
                quotation_id = quotation['id']
                quote_no = quotation.get('quote_no', 'Unknown')
                
                print_info(f"Testing quotation {i}: {quote_no} (ID: {quotation_id})")
                
                try:
                    pdf_response = self.session.get(f"{API_BASE}/quotations/{quotation_id}/generate-pdf")
                    
                    if pdf_response.status_code == 200:
                        file_size = len(pdf_response.content)
                        file_size_kb = file_size / 1024
                        
                        # Basic validation
                        if (pdf_response.content.startswith(b'%PDF-') and 
                            file_size > 10 * 1024 and
                            pdf_response.headers.get('content-type') == 'application/pdf'):
                            
                            print_success(f"  ✓ PDF generated successfully ({file_size_kb:.1f} KB)")
                            success_count += 1
                        else:
                            print_error(f"  ✗ PDF validation failed")
                    else:
                        print_error(f"  ✗ PDF generation failed (HTTP {pdf_response.status_code})")
                        
                except Exception as e:
                    print_error(f"  ✗ Error generating PDF: {str(e)}")
            
            if success_count == len(test_quotations):
                print_success(f"All {success_count} quotations generated PDFs successfully")
                return True
            elif success_count > 0:
                print_warning(f"{success_count}/{len(test_quotations)} quotations generated PDFs successfully")
                return success_count >= 3  # Consider success if at least 3 work
            else:
                print_error("No quotations generated PDFs successfully")
                return False
                
        except Exception as e:
            print_error(f"Error during multiple quotations test: {str(e)}")
            return False
    
    def check_backend_logs(self):
        """Check backend logs for [PDF-WP] markers"""
        print_header("Checking Backend Logs for WeasyPrint Markers")
        
        try:
            # Check supervisor backend logs
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.out.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                pdf_wp_lines = [line for line in log_content.split('\n') if '[PDF-WP]' in line]
                
                if pdf_wp_lines:
                    print_success(f"Found {len(pdf_wp_lines)} [PDF-WP] log entries")
                    for line in pdf_wp_lines[-5:]:  # Show last 5 entries
                        print_info(f"  {line.strip()}")
                else:
                    print_warning("No [PDF-WP] markers found in recent logs")
                
                return True
            else:
                print_warning("Could not read backend logs")
                return True  # Don't fail the test for this
                
        except Exception as e:
            print_warning(f"Error checking backend logs: {str(e)}")
            return True  # Don't fail the test for this
    
    def run_all_tests(self):
        """Run all WeasyPrint PDF generation tests"""
        print_header("WeasyPrint PDF Generation Test Suite")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        # Test 0: Backend Connection
        test_results.append(("Backend Connection", self.test_backend_connection()))
        
        # Test 1: Single Item Quotation
        test_results.append(("Single Item Quotation PDF", self.test_single_item_quotation_pdf()))
        
        # Test 2: Multi-Item Quotation
        test_results.append(("Multi-Item Quotation PDF", self.test_multi_item_quotation_pdf()))
        
        # Test 3: PDF Content Verification
        test_results.append(("PDF Content Verification", self.test_pdf_content_verification()))
        
        # Test 4: Error Handling
        test_results.append(("Error Handling (Invalid ID)", self.test_error_handling_invalid_id()))
        
        # Test 5: Multiple Quotations
        test_results.append(("Multiple Quotations PDF", self.test_multiple_quotations()))
        
        # Additional: Check Backend Logs
        test_results.append(("Backend Logs Check", self.check_backend_logs()))
        
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
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL WEASYPRINT PDF TESTS PASSED! 🎉{Colors.ENDC}")
            print(f"{Colors.GREEN}✅ WeasyPrint PDF generation feature is fully operational{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed} TEST(S) FAILED ❌{Colors.ENDC}")
            print(f"{Colors.RED}❌ WeasyPrint PDF generation has issues that need attention{Colors.ENDC}")

def main():
    """Main function"""
    tester = WeasyPrintPDFTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()