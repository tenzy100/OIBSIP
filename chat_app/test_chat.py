#!/usr/bin/env python3
"""
Test script for Chat Application
Tests user registration and basic functionality
"""

import requests
import json

BASE_URL = "http://localhost:3200"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")

    # Test data
    test_user = {
        "username": "testuser",
        "password": "testpass123",
        "confirm": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/register", data=test_user)
    print(f"Registration status: {response.status_code}")

    if response.status_code == 200:
        print("✅ User registration successful")
        return True
    else:
        print(f"❌ Registration failed: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("Testing user login...")

    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"Login status: {response.status_code}")

    if response.status_code == 302:  # Redirect to main page
        print("✅ User login successful")
        return True
    else:
        print(f"❌ Login failed: {response.text}")
        return False

def test_api_access():
    """Test API access with authentication"""
    print("Testing API access...")

    # First login to get session
    session = requests.Session()
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    # Login
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)

    if login_response.status_code != 302:
        print("❌ Could not login for API test")
        return False

    # Test rooms API
    rooms_response = session.get(f"{BASE_URL}/api/rooms")
    print(f"Rooms API status: {rooms_response.status_code}")

    if rooms_response.status_code == 200:
        rooms_data = rooms_response.json()
        print(f"✅ Found {len(rooms_data)} chat rooms")
        for room in rooms_data:
            print(f"   - {room['name']}")
        return True
    else:
        print(f"❌ Rooms API failed: {rooms_response.text}")
        return False

def main():
    """Run all tests"""
    print("🧪 Chat Application Test Suite")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test 1: Registration
    if test_registration():
        tests_passed += 1

    print()

    # Test 2: Login
    if test_login():
        tests_passed += 1

    print()

    # Test 3: API Access
    if test_api_access():
        tests_passed += 1

    print()
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 All tests passed! Chat application is working correctly.")
        print(f"🌐 You can access the application at: {BASE_URL}")
        print("📝 Register a new account or login with 'testuser' / 'testpass123'")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
