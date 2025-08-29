#!/usr/bin/env python3
"""
Simple JIRA Filter Management Tool

A clean, easy-to-read script for listing and deleting JIRA filters.
Focus on core functionality with minimal complexity.

ENVIRONMENT VARIABLES:
    JIRA_URL            - Your JIRA instance URL (e.g., https://issues.redhat.com)
    JIRA_USERNAME       - Your JIRA username or email 
    JIRA_API_TOKEN      - Your JIRA API token or Personal Access Token

USAGE:
    1. Set environment variables
    2. Run: python3 simple_delete_jira_filters.py
    3. View numbered list of your filters
    4. Select filters to delete using ranges (1-5, 2,4,7, etc.)

EXAMPLES:
    export JIRA_URL="https://issues.redhat.com"
    export JIRA_USERNAME="your-email@redhat.com"
    export JIRA_API_TOKEN="your-personal-access-token"
    python3 simple_delete_jira_filters.py
"""

import requests
import os
import sys


class SimpleJiraManager:
    """Simple JIRA manager focused on filter operations"""
    
    def __init__(self, jira_url, username, api_token):
        self.jira_url = jira_url.rstrip('/')
        self.session = requests.Session()
        
        # Auto-detect authentication method
        if 'issues.redhat.com' in jira_url.lower():
            # Red Hat JIRA uses Bearer token
            self.session.headers.update({
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            })
        else:
            # Standard JIRA uses Basic auth
            self.session.auth = (username, api_token)
            self.session.headers.update({'Content-Type': 'application/json'})
    
    def get_my_filters(self):
        """Get all filters owned by the current user"""
        url = f"{self.jira_url}/rest/api/2/filter/favourite"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting filters: {e}")
            return None
    
    def delete_filter(self, filter_id):
        """Delete a filter by ID"""
        url = f"{self.jira_url}/rest/api/2/filter/{filter_id}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting filter {filter_id}: {e}")
            return False


def get_credentials():
    """Get JIRA credentials from environment variables"""
    jira_url = os.getenv('JIRA_URL')
    username = os.getenv('JIRA_USERNAME')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    missing = []
    if not jira_url:
        missing.append('JIRA_URL')
    if not username:
        missing.append('JIRA_USERNAME')
    if not api_token:
        missing.append('JIRA_API_TOKEN')
    
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        print("\nExample setup:")
        print("export JIRA_URL='https://issues.redhat.com'")
        print("export JIRA_USERNAME='your-email@company.com'")
        print("export JIRA_API_TOKEN='your-personal-access-token'")
        sys.exit(1)
    
    return jira_url, username, api_token


def display_filters(filters):
    """Display filters in a numbered list"""
    print(f"\nYour JIRA Filters ({len(filters)}):")
    print("-" * 60)
    
    for i, filter_item in enumerate(filters, 1):
        name = filter_item.get('name', 'Unknown')
        filter_id = filter_item.get('id', 'Unknown')
        owner = filter_item.get('owner', {}).get('displayName', 'Unknown')
        
        print(f"{i:2}. {name}")
        print(f"    ID: {filter_id} | Owner: {owner}")
    
    print("-" * 60)


def parse_selection(selection, max_count):
    """Parse user selection string into list of indices
    
    Examples: '1-5' -> [1,2,3,4,5], '2,4,7' -> [2,4,7], '1-3,6' -> [1,2,3,6]
    """
    selected = set()
    
    try:
        # Split by commas and process each part
        parts = [part.strip() for part in selection.split(',')]
        
        for part in parts:
            if '-' in part:
                # Handle range (e.g., '1-5')
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                
                if start < 1 or end > max_count or start > end:
                    return None, f"Invalid range: {part}"
                
                selected.update(range(start, end + 1))
            else:
                # Handle single number
                num = int(part.strip())
                if num < 1 or num > max_count:
                    return None, f"Invalid number: {num}"
                selected.add(num)
        
        return sorted(list(selected)), None
        
    except ValueError:
        return None, "Invalid format. Use: 1-5, 2,4,7, or 1-3,6"


def confirm_deletion(filters_to_delete):
    """Ask user to confirm deletion"""
    count = len(filters_to_delete)
    
    print(f"\nYou are about to delete {count} filter(s):")
    for filter_item in filters_to_delete:
        name = filter_item.get('name', 'Unknown')
        filter_id = filter_item.get('id', 'Unknown')
        print(f"  - {name} (ID: {filter_id})")
    
    while True:
        response = input(f"\nDelete these {count} filter(s)? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def main():
    """Main function - simple and clean"""
    print("Simple JIRA Filter Management Tool")
    print("=" * 40)
    
    # Get credentials
    jira_url, username, api_token = get_credentials()
    jira = SimpleJiraManager(jira_url, username, api_token)
    
    print(f"Connected to: {jira_url}")
    
    # Get and display filters
    print("\nLoading your filters...")
    filters = jira.get_my_filters()
    
    if not filters:
        print("No filters found or error occurred.")
        sys.exit(1)
    
    if len(filters) == 0:
        print("You have no filters to manage.")
        sys.exit(0)
    
    display_filters(filters)
    
    # Get user selection
    print("\nSelection examples:")
    print("  Single: 3")
    print("  Range: 1-5") 
    print("  Multiple: 2,4,7")
    print("  Combined: 1-3,6-8")
    print("  All: 1-" + str(len(filters)))
    
    try:
        selection = input(f"\nSelect filters to delete (1-{len(filters)}): ").strip()
        if not selection:
            print("No selection made. Exiting.")
            sys.exit(0)
        
        # Parse selection
        indices, error = parse_selection(selection, len(filters))
        if error:
            print(f"Error: {error}")
            sys.exit(1)
        
        # Get selected filters
        selected_filters = [filters[i-1] for i in indices]
        
        # Confirm deletion
        if not confirm_deletion(selected_filters):
            print("Deletion cancelled.")
            sys.exit(0)
        
        # Delete filters
        print(f"\nDeleting {len(selected_filters)} filter(s)...")
        
        successful = 0
        failed = 0
        
        for filter_item in selected_filters:
            name = filter_item.get('name', 'Unknown')
            filter_id = filter_item.get('id')
            
            print(f"  Deleting '{name}'... ", end='')
            if jira.delete_filter(filter_id):
                print("✓")
                successful += 1
            else:
                print("✗")
                failed += 1
        
        # Summary
        print(f"\nResults: {successful} deleted, {failed} failed")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
