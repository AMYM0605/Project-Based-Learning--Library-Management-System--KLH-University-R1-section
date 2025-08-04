#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Library Management System
Tests all core functionalities including authentication, book management, 
borrowing system, AI/ML features, and dashboard analytics.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Backend URL from frontend/.env
BASE_URL = "https://c6e5edec-cca6-444b-8ec3-d692bd338180.preview.emergentagent.com/api"

class LibraryAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.librarian_token = None
        self.member_token = None
        self.librarian_user = None
        self.member_user = None
        self.test_book_id = None
        self.test_borrow_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "book_management": {"passed": 0, "failed": 0, "details": []},
            "user_management": {"passed": 0, "failed": 0, "details": []},
            "borrowing_system": {"passed": 0, "failed": 0, "details": []},
            "ai_features": {"passed": 0, "failed": 0, "details": []},
            "dashboard": {"passed": 0, "failed": 0, "details": []}
        }

    def log_result(self, category: str, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return False, {"error": "Invalid method"}, 400

            return response.status_code < 400, response.json() if response.content else {}, response.status_code
        except Exception as e:
            return False, {"error": str(e)}, 500

    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}

    def test_authentication_system(self):
        """Test authentication endpoints"""
        print("\n=== Testing Authentication System ===")
        
        # Test librarian registration
        librarian_data = {
            "name": "Sarah Johnson",
            "email": "sarah.librarian@library.edu",
            "password": "LibraryAdmin2024!",
            "role": "librarian"
        }
        
        success, response, status = self.make_request("POST", "/auth/register", librarian_data)
        if success and "access_token" in response:
            self.librarian_token = response["access_token"]
            self.librarian_user = response["user"]
            self.log_result("authentication", "Librarian Registration", True, f"User ID: {self.librarian_user['id']}")
        else:
            self.log_result("authentication", "Librarian Registration", False, f"Status: {status}, Response: {response}")

        # Test member registration
        member_data = {
            "name": "Michael Chen",
            "email": "michael.reader@email.com",
            "password": "BookLover2024!",
            "role": "member"
        }
        
        success, response, status = self.make_request("POST", "/auth/register", member_data)
        if success and "access_token" in response:
            self.member_token = response["access_token"]
            self.member_user = response["user"]
            self.log_result("authentication", "Member Registration", True, f"User ID: {self.member_user['id']}")
        else:
            self.log_result("authentication", "Member Registration", False, f"Status: {status}, Response: {response}")

        # Test librarian login
        login_data = {
            "email": "sarah.librarian@library.edu",
            "password": "LibraryAdmin2024!"
        }
        
        success, response, status = self.make_request("POST", "/auth/login", login_data)
        if success and "access_token" in response:
            self.log_result("authentication", "Librarian Login", True, "Login successful")
        else:
            self.log_result("authentication", "Librarian Login", False, f"Status: {status}, Response: {response}")

        # Test member login
        login_data = {
            "email": "michael.reader@email.com",
            "password": "BookLover2024!"
        }
        
        success, response, status = self.make_request("POST", "/auth/login", login_data)
        if success and "access_token" in response:
            self.log_result("authentication", "Member Login", True, "Login successful")
        else:
            self.log_result("authentication", "Member Login", False, f"Status: {status}, Response: {response}")

        # Test protected endpoint - get current user
        if self.librarian_token:
            headers = self.get_auth_headers(self.librarian_token)
            success, response, status = self.make_request("GET", "/auth/me", headers=headers)
            if success and response.get("role") == "librarian":
                self.log_result("authentication", "Protected Endpoint Access", True, "Librarian profile retrieved")
            else:
                self.log_result("authentication", "Protected Endpoint Access", False, f"Status: {status}, Response: {response}")

    def test_book_management(self):
        """Test book management CRUD operations"""
        print("\n=== Testing Book Management ===")
        
        if not self.librarian_token:
            self.log_result("book_management", "Book Management Tests", False, "No librarian token available")
            return

        headers = self.get_auth_headers(self.librarian_token)

        # Test create book (librarian only)
        book_data = {
            "title": "The Art of Software Engineering",
            "author": "Dr. Emily Rodriguez",
            "isbn": "978-0123456789",
            "genre": "Technology",
            "publication_year": 2023,
            "description": "A comprehensive guide to modern software engineering practices and methodologies.",
            "total_copies": 5,
            "tags": ["programming", "software", "engineering", "technology"]
        }
        
        success, response, status = self.make_request("POST", "/books", book_data, headers)
        if success and "id" in response:
            self.test_book_id = response["id"]
            self.log_result("book_management", "Create Book", True, f"Book created with ID: {self.test_book_id}")
        else:
            self.log_result("book_management", "Create Book", False, f"Status: {status}, Response: {response}")

        # Test get all books
        success, response, status = self.make_request("GET", "/books")
        if success and isinstance(response, list):
            self.log_result("book_management", "Get All Books", True, f"Retrieved {len(response)} books")
        else:
            self.log_result("book_management", "Get All Books", False, f"Status: {status}, Response: {response}")

        # Test search books by title
        success, response, status = self.make_request("GET", "/books", {"search": "Software"})
        if success and isinstance(response, list):
            found_book = any(book.get("title", "").lower().find("software") != -1 for book in response)
            self.log_result("book_management", "Search Books by Title", found_book, f"Found {len(response)} books")
        else:
            self.log_result("book_management", "Search Books by Title", False, f"Status: {status}, Response: {response}")

        # Test search books by genre
        success, response, status = self.make_request("GET", "/books", {"genre": "Technology"})
        if success and isinstance(response, list):
            self.log_result("book_management", "Search Books by Genre", True, f"Found {len(response)} technology books")
        else:
            self.log_result("book_management", "Search Books by Genre", False, f"Status: {status}, Response: {response}")

        # Test get specific book
        if self.test_book_id:
            success, response, status = self.make_request("GET", f"/books/{self.test_book_id}")
            if success and response.get("id") == self.test_book_id:
                self.log_result("book_management", "Get Specific Book", True, f"Retrieved book: {response.get('title')}")
            else:
                self.log_result("book_management", "Get Specific Book", False, f"Status: {status}, Response: {response}")

        # Test update book
        if self.test_book_id:
            update_data = {
                "description": "Updated: A comprehensive guide to modern software engineering practices, methodologies, and best practices for 2024."
            }
            success, response, status = self.make_request("PUT", f"/books/{self.test_book_id}", update_data, headers)
            if success:
                self.log_result("book_management", "Update Book", True, "Book description updated")
            else:
                self.log_result("book_management", "Update Book", False, f"Status: {status}, Response: {response}")

        # Test member cannot create book
        if self.member_token:
            member_headers = self.get_auth_headers(self.member_token)
            success, response, status = self.make_request("POST", "/books", book_data, member_headers)
            if not success and status == 403:
                self.log_result("book_management", "Member Create Book Restriction", True, "Correctly blocked member from creating book")
            else:
                self.log_result("book_management", "Member Create Book Restriction", False, f"Member was able to create book: {status}")

    def test_user_management(self):
        """Test user management operations"""
        print("\n=== Testing User Management ===")
        
        if not self.librarian_token:
            self.log_result("user_management", "User Management Tests", False, "No librarian token available")
            return

        headers = self.get_auth_headers(self.librarian_token)

        # Test get all users (librarian only)
        success, response, status = self.make_request("GET", "/users", headers=headers)
        if success and isinstance(response, list):
            self.log_result("user_management", "Get All Users", True, f"Retrieved {len(response)} users")
        else:
            self.log_result("user_management", "Get All Users", False, f"Status: {status}, Response: {response}")

        # Test member cannot access user list
        if self.member_token:
            member_headers = self.get_auth_headers(self.member_token)
            success, response, status = self.make_request("GET", "/users", headers=member_headers)
            if not success and status == 403:
                self.log_result("user_management", "Member User Access Restriction", True, "Correctly blocked member from accessing user list")
            else:
                self.log_result("user_management", "Member User Access Restriction", False, f"Member was able to access users: {status}")

    def test_borrowing_system(self):
        """Test borrowing and returning system"""
        print("\n=== Testing Borrowing System ===")
        
        if not self.member_token or not self.test_book_id:
            self.log_result("borrowing_system", "Borrowing System Tests", False, "Missing member token or test book")
            return

        member_headers = self.get_auth_headers(self.member_token)

        # Test borrow book
        borrow_data = {
            "book_id": self.test_book_id,
            "borrow_days": 14
        }
        
        success, response, status = self.make_request("POST", "/borrow", borrow_data, member_headers)
        if success and "id" in response:
            self.test_borrow_id = response["id"]
            self.log_result("borrowing_system", "Borrow Book", True, f"Book borrowed with ID: {self.test_borrow_id}")
        else:
            self.log_result("borrowing_system", "Borrow Book", False, f"Status: {status}, Response: {response}")

        # Test get user's borrows
        success, response, status = self.make_request("GET", "/borrows", headers=member_headers)
        if success and isinstance(response, list):
            user_borrows = [b for b in response if b.get("user_id") == self.member_user["id"]]
            self.log_result("borrowing_system", "Get User Borrows", True, f"User has {len(user_borrows)} borrows")
        else:
            self.log_result("borrowing_system", "Get User Borrows", False, f"Status: {status}, Response: {response}")

        # Test duplicate borrow prevention
        success, response, status = self.make_request("POST", "/borrow", borrow_data, member_headers)
        if not success and status == 400:
            self.log_result("borrowing_system", "Duplicate Borrow Prevention", True, "Correctly prevented duplicate borrow")
        else:
            self.log_result("borrowing_system", "Duplicate Borrow Prevention", False, f"Duplicate borrow was allowed: {status}")

        # Test return book
        if self.test_borrow_id:
            return_data = {
                "borrow_id": self.test_borrow_id
            }
            success, response, status = self.make_request("POST", "/return", return_data, member_headers)
            if success:
                fine_amount = response.get("fine_amount", 0)
                self.log_result("borrowing_system", "Return Book", True, f"Book returned, fine: ${fine_amount}")
            else:
                self.log_result("borrowing_system", "Return Book", False, f"Status: {status}, Response: {response}")

        # Test librarian can view all borrows
        if self.librarian_token:
            librarian_headers = self.get_auth_headers(self.librarian_token)
            success, response, status = self.make_request("GET", "/borrows", headers=librarian_headers)
            if success and isinstance(response, list):
                self.log_result("borrowing_system", "Librarian View All Borrows", True, f"Librarian can see {len(response)} total borrows")
            else:
                self.log_result("borrowing_system", "Librarian View All Borrows", False, f"Status: {status}, Response: {response}")

        # Test overdue books (librarian only)
        if self.librarian_token:
            librarian_headers = self.get_auth_headers(self.librarian_token)
            success, response, status = self.make_request("GET", "/overdue", headers=librarian_headers)
            if success and isinstance(response, list):
                self.log_result("borrowing_system", "Get Overdue Books", True, f"Found {len(response)} overdue books")
            else:
                self.log_result("borrowing_system", "Get Overdue Books", False, f"Status: {status}, Response: {response}")

    def test_ai_features(self):
        """Test AI/ML features"""
        print("\n=== Testing AI/ML Features ===")
        
        # Test book recommendations
        if self.member_user:
            success, response, status = self.make_request("GET", f"/recommendations/{self.member_user['id']}")
            if success and isinstance(response, list):
                self.log_result("ai_features", "Book Recommendations", True, f"Generated {len(response)} recommendations")
            else:
                self.log_result("ai_features", "Book Recommendations", False, f"Status: {status}, Response: {response}")

        # Test demand forecasting (librarian only)
        if self.librarian_token:
            librarian_headers = self.get_auth_headers(self.librarian_token)
            success, response, status = self.make_request("GET", "/analytics/demand-forecast", headers=librarian_headers)
            if success and isinstance(response, list):
                self.log_result("ai_features", "Demand Forecasting", True, f"Generated forecasts for {len(response)} books")
            else:
                self.log_result("ai_features", "Demand Forecasting", False, f"Status: {status}, Response: {response}")

        # Test overdue predictions (librarian only)
        if self.librarian_token:
            librarian_headers = self.get_auth_headers(self.librarian_token)
            success, response, status = self.make_request("GET", "/analytics/overdue-predictions", headers=librarian_headers)
            if success and isinstance(response, list):
                self.log_result("ai_features", "Overdue Predictions", True, f"Generated {len(response)} overdue predictions")
            else:
                self.log_result("ai_features", "Overdue Predictions", False, f"Status: {status}, Response: {response}")

        # Test member cannot access analytics
        if self.member_token:
            member_headers = self.get_auth_headers(self.member_token)
            success, response, status = self.make_request("GET", "/analytics/demand-forecast", headers=member_headers)
            if not success and status == 403:
                self.log_result("ai_features", "Member Analytics Restriction", True, "Correctly blocked member from analytics")
            else:
                self.log_result("ai_features", "Member Analytics Restriction", False, f"Member accessed analytics: {status}")

    def test_dashboard_analytics(self):
        """Test dashboard analytics"""
        print("\n=== Testing Dashboard Analytics ===")
        
        if not self.librarian_token:
            self.log_result("dashboard", "Dashboard Tests", False, "No librarian token available")
            return

        librarian_headers = self.get_auth_headers(self.librarian_token)

        # Test dashboard stats
        success, response, status = self.make_request("GET", "/dashboard/stats", headers=librarian_headers)
        if success and "total_books" in response:
            stats = response
            self.log_result("dashboard", "Dashboard Statistics", True, 
                          f"Books: {stats.get('total_books')}, Users: {stats.get('total_users')}, "
                          f"Active Borrows: {stats.get('active_borrows')}, Overdue: {stats.get('overdue_books')}")
        else:
            self.log_result("dashboard", "Dashboard Statistics", False, f"Status: {status}, Response: {response}")

        # Test member cannot access dashboard
        if self.member_token:
            member_headers = self.get_auth_headers(self.member_token)
            success, response, status = self.make_request("GET", "/dashboard/stats", headers=member_headers)
            if not success and status == 403:
                self.log_result("dashboard", "Member Dashboard Restriction", True, "Correctly blocked member from dashboard")
            else:
                self.log_result("dashboard", "Member Dashboard Restriction", False, f"Member accessed dashboard: {status}")

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        if self.librarian_token and self.test_book_id:
            headers = self.get_auth_headers(self.librarian_token)
            success, response, status = self.make_request("DELETE", f"/books/{self.test_book_id}", headers=headers)
            if success:
                print("✅ Test book deleted successfully")
            else:
                print(f"❌ Failed to delete test book: {status}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Library Management System Backend API Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Run tests in order
        self.test_authentication_system()
        self.test_book_management()
        self.test_user_management()
        self.test_borrowing_system()
        self.test_ai_features()
        self.test_dashboard_analytics()
        
        # Clean up
        self.cleanup_test_data()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "❌" if passed == 0 else "⚠️"
            print(f"{status_icon} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            # Print details for failed tests
            if failed > 0:
                for detail in results["details"]:
                    if "❌ FAIL" in detail:
                        print(f"   {detail}")
        
        print("-" * 80)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {total_passed} passed, {total_failed} failed - {overall_status}")
        print("=" * 80)

if __name__ == "__main__":
    tester = LibraryAPITester()
    tester.run_all_tests()