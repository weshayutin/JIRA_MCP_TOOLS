#!/usr/bin/env python3
"""
Simple test script to verify Jira authentication
"""

import requests
import os
import sys

def test_jira_auth():
    """Test basic Jira authentication"""
    
    jira_url = os.getenv('JIRA_URL')
    username = os.getenv('JIRA_USERNAME') 
    api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, username, api_token]):
        print("❌ Missing environment variables:")
        print(f"   JIRA_URL: {'✅' if jira_url else '❌'}")
        print(f"   JIRA_USERNAME: {'✅' if username else '❌'}")  
        print(f"   JIRA_API_TOKEN: {'✅' if api_token else '❌'}")
        return False
    
    print(f"🔗 Testing connection to: {jira_url}")
    print(f"👤 Username: {username}")
    print(f"🔑 API Token: {api_token[:10]}...{api_token[-10:]}")
    
    # Test with basic auth
    auth = (username, api_token)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test different endpoints
    test_endpoints = [
        '/rest/api/2/myself',
        '/rest/api/2/serverInfo', 
        '/rest/api/2/filter/search?maxResults=1'
    ]
    
    for endpoint in test_endpoints:
        url = f"{jira_url}{endpoint}"
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        try:
            response = requests.get(url, auth=auth, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
                try:
                    data = response.json()
                    if endpoint == '/rest/api/2/myself':
                        print(f"   User: {data.get('displayName', 'N/A')}")
                        print(f"   Email: {data.get('emailAddress', 'N/A')}")
                    elif endpoint == '/rest/api/2/serverInfo':
                        print(f"   Server: {data.get('serverTitle', 'N/A')}")
                        print(f"   Version: {data.get('version', 'N/A')}")
                except:
                    print("   (Non-JSON response)")
            else:
                print(f"   ❌ FAILED: {response.reason}")
                if response.status_code == 401:
                    print("   Authentication failed - check your credentials")
                elif response.status_code == 403:
                    print("   Access forbidden - check permissions")
                elif response.status_code == 404:
                    print("   Endpoint not found - might be different API version")
                    
                try:
                    error_data = response.json()
                    if 'errorMessages' in error_data:
                        for msg in error_data['errorMessages']:
                            print(f"   Error: {msg}")
                except:
                    print(f"   Response: {response.text[:200]}...")
                    
        except requests.exceptions.ConnectionError:
            print("   ❌ CONNECTION ERROR - Check URL and network")
        except requests.exceptions.Timeout:
            print("   ❌ TIMEOUT - Server took too long to respond")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    return True

if __name__ == "__main__":
    print("🔧 Jira Authentication Test")
    print("=" * 40)
    test_jira_auth()
