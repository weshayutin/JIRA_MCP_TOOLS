#!/usr/bin/env python3
"""
Test script specifically for Red Hat Jira authentication methods
"""

import requests
import os
import sys
import base64

def test_redhat_jira():
    """Test different authentication methods for Red Hat Jira"""
    
    jira_url = os.getenv('JIRA_URL', 'https://issues.redhat.com')
    username = os.getenv('JIRA_USERNAME')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    print(f"🔗 Testing Red Hat Jira: {jira_url}")
    print(f"👤 Username: {username}")
    
    # Test 1: Check server info without auth
    print("\n🔍 Test 1: Server info (no auth)")
    try:
        response = requests.get(f"{jira_url}/rest/api/2/serverInfo", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Server: {data.get('serverTitle', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Try different auth headers
    print(f"\n🔍 Test 2: Basic Auth with API token")
    auth_methods = [
        ("Basic Auth (username:token)", (username, api_token)),
        ("Basic Auth (email:token)", (username, api_token)),
    ]
    
    for auth_name, auth_tuple in auth_methods:
        print(f"\n   Testing: {auth_name}")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{jira_url}/rest/api/2/myself", 
                auth=auth_tuple, 
                headers=headers, 
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                print(f"   User: {data.get('displayName', 'N/A')}")
                return True
            else:
                print(f"   ❌ Failed: {response.reason}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 3: Try Bearer token
    print(f"\n🔍 Test 3: Bearer Token")
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(f"{jira_url}/rest/api/2/myself", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS!")
            return True
        else:
            print(f"   ❌ Failed: {response.reason}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check what auth methods are supported
    print(f"\n🔍 Test 4: Check authentication requirements")
    try:
        response = requests.get(f"{jira_url}/rest/api/2/myself", timeout=10)
        print(f"   Status: {response.status_code}")
        print("   Response headers:")
        for header, value in response.headers.items():
            if 'auth' in header.lower() or 'www-' in header.lower():
                print(f"     {header}: {value}")
        
        if 'WWW-Authenticate' in response.headers:
            print(f"\n   Server expects: {response.headers['WWW-Authenticate']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Check if it's using OAuth or session auth
    print(f"\n🔍 Test 5: Check for OAuth/Session endpoints")
    oauth_endpoints = [
        '/plugins/servlet/oauth/authorize',
        '/rest/auth/1/session',
        '/rest/api/2/auth',
        '/login.jsp'
    ]
    
    for endpoint in oauth_endpoints:
        try:
            response = requests.get(f"{jira_url}{endpoint}", timeout=5, allow_redirects=False)
            if response.status_code not in [404, 500]:
                print(f"   Found: {endpoint} (Status: {response.status_code})")
        except:
            pass
    
    print(f"\n💡 Red Hat Jira may require:")
    print("   1. Kerberos authentication (for internal Red Hat users)")
    print("   2. Session-based authentication via web login")
    print("   3. Personal Access Token instead of API token")
    print("   4. OAuth authentication")
    print("   5. VPN access if you're external to Red Hat")
    
    return False

if __name__ == "__main__":
    print("🔧 Red Hat Jira Authentication Test")
    print("=" * 45)
    test_redhat_jira()
