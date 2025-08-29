#!/usr/bin/env python3
"""
Script to delete Jira filters and boards with user confirmation.
Searches for filters/boards and prompts user before deletion.
Supports single and batch deletion with range selection.

FEATURES:
    📋 FILTERS:
    • Search filters by name
    • List all your filters  
    • Delete individual filters or ranges/batches
    
    📊 BOARDS:
    • Search boards by configurable filter (server-side API filtering)
    • List all boards
    • Delete individual boards or ranges/batches
    
    🎯 COMMON:
    • Range selection support: 1-5, 2,4,7, 1-3,6-8,10, etc.
    • Confirmation prompts before deletion
    • Detailed information display
    • Progress tracking for batch operations

ENVIRONMENT VARIABLES:
    JIRA_URL         - Your Jira instance URL (e.g., https://company.atlassian.net)  
    JIRA_USERNAME    - Your Jira username or email address
    JIRA_EMAIL       - Alternative to JIRA_USERNAME  
    JIRA_USER        - Alternative to JIRA_USERNAME
    JIRA_API_TOKEN   - Your Jira API token or Personal Access Token
                       • Atlassian Cloud: API token from id.atlassian.com/manage-profile/security/api-tokens
                       • Red Hat Jira: Personal Access Token (auto-detected, uses Bearer auth)
    JIRA_TOKEN       - Alternative to JIRA_API_TOKEN
    JIRA_BOARD_FILTER - Board name filter for option 4 (required)
                        Set this to search for boards containing a specific substring

USAGE EXAMPLES:
    # Set environment variables and run
    export JIRA_URL="https://company.atlassian.net"
    export JIRA_USERNAME="user@company.com" 
    export JIRA_API_TOKEN="your-api-token"
    export JIRA_BOARD_FILTER="myproject"  # Required: filter for board search
    python3 delete_jira_filters.py
    
    # Or run interactively (will prompt for missing values)
    python3 delete_jira_filters.py
    
    # Range selection examples when prompted:
    3           # Delete item 3
    1-5         # Delete items 1 through 5
    2,4,7       # Delete items 2, 4, and 7
    1-3,6-8,10  # Delete items 1-3, 6-8, and 10
    
    # Board Filter Search (Option 4):
    # Uses JIRA_BOARD_FILTER environment variable (required)
    # Server-side case-insensitive search finds boards containing the filter string
    # Example: filter "myproject" finds "MyProject-Dev", "myproject-testing", etc.

REQUIREMENTS:
    pip install requests
"""

import requests
import json
import sys
import os
from urllib.parse import quote
import getpass


class JiraManager:
    def __init__(self, jira_url, username, api_token, use_bearer_token=False):
        self.jira_url = jira_url.rstrip('/')
        self.session = requests.Session()
        
        # Determine auth method based on server (Red Hat Jira uses Bearer tokens)
        if 'issues.redhat.com' in jira_url.lower() or use_bearer_token:
            # Use Bearer token authentication (Red Hat Jira)
            self.session.headers.update({
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            print("🔑 Using Bearer Token authentication")
        else:
            # Use Basic authentication (Atlassian Cloud)
            self.auth = (username, api_token)
            self.session.auth = self.auth
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            print("🔑 Using Basic Auth authentication")

    def search_filters(self, filter_name=None, owner=None):
        """Search for filters by name or owner"""
        url = f"{self.jira_url}/rest/api/2/filter/search"
        params = {}
        
        if filter_name:
            params['filterName'] = filter_name
        if owner:
            params['owner'] = owner
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching filters: {e}")
            return None

    def get_filter_details(self, filter_id):
        """Get detailed information about a filter"""
        url = f"{self.jira_url}/rest/api/2/filter/{filter_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting filter details: {e}")
            return None

    def delete_filter(self, filter_id):
        """Delete a filter by ID"""
        url = f"{self.jira_url}/rest/api/2/filter/{filter_id}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error deleting filter: {e}")
            return False

    def list_my_filters(self):
        """List all filters owned by the current user"""
        url = f"{self.jira_url}/rest/api/2/filter/favourite"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error listing filters: {e}")
            return None

    def list_boards(self, board_type=None, project_key=None):
        """List all boards accessible to the current user"""
        url = f"{self.jira_url}/rest/agile/1.0/board"
        params = {}
        
        if board_type:
            params['type'] = board_type
        if project_key:
            params['projectKeyOrId'] = project_key
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error listing boards: {e}")
            return None

    def get_board_details(self, board_id):
        """Get detailed information about a board"""
        url = f"{self.jira_url}/rest/agile/1.0/board/{board_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting board details: {e}")
            return None

    def delete_board(self, board_id):
        """Delete a board by ID"""
        url = f"{self.jira_url}/rest/agile/1.0/board/{board_id}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error deleting board: {e}")
            return False

    def search_boards(self, board_name=None, board_type=None):
        """Search for boards by name or type"""
        url = f"{self.jira_url}/rest/agile/1.0/board"
        params = {}
        
        if board_name:
            params['name'] = board_name
        if board_type:
            params['type'] = board_type
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching boards: {e}")
            return None


def get_jira_credentials():
    """Get Jira credentials from environment variables or prompt user if missing
    
    Environment variables supported:
    - JIRA_URL: Your Jira instance URL (e.g., https://company.atlassian.net)
    - JIRA_USERNAME or JIRA_EMAIL: Your Jira username or email
    - JIRA_API_TOKEN: Your Jira API token
    
    Note: JIRA_BOARD_FILTER is also required and handled separately
    """
    print("🔐 Checking for Jira credentials...")
    
    # Try to get from environment variables
    jira_url = os.getenv('JIRA_URL')
    username = os.getenv('JIRA_USERNAME') or os.getenv('JIRA_EMAIL') or os.getenv('JIRA_USER')
    api_token = os.getenv('JIRA_API_TOKEN') or os.getenv('JIRA_TOKEN')
    
    # Show what was found
    env_found = []
    if jira_url:
        env_found.append("JIRA_URL")
    if username:
        env_found.append("JIRA_USERNAME/JIRA_EMAIL")
    if api_token:
        env_found.append("JIRA_API_TOKEN")
    
    if env_found:
        print(f"✅ Found environment variables: {', '.join(env_found)}")
        print("📝 Note: JIRA_BOARD_FILTER is also required (checked separately)")
    
    # Prompt for missing values
    if not jira_url:
        print("❌ JIRA_URL not found in environment")
        jira_url = input("Enter your Jira URL (e.g., https://company.atlassian.net): ").strip()
    else:
        print(f"🌐 Using Jira URL: {jira_url}")
    
    if not username:
        print("❌ JIRA_USERNAME/JIRA_EMAIL not found in environment")
        username = input("Enter your Jira username/email: ").strip()
    else:
        print(f"👤 Using username: {username}")
    
    if not api_token:
        print("❌ JIRA_API_TOKEN not found in environment")
        api_token = getpass.getpass("Enter your Jira API token: ").strip()
    else:
        print("🔑 Using API token from environment")
    
    return jira_url, username, api_token


def get_board_filter():
    """Get board filter from environment variable or prompt user if missing"""
    board_filter = os.getenv('JIRA_BOARD_FILTER')
    
    if board_filter:
        print(f"🔍 Using board filter from environment: '{board_filter}'")
    else:
        print("❌ JIRA_BOARD_FILTER not found in environment")
        board_filter = input("Enter board name filter for search option 4: ").strip()
        if not board_filter:
            print("❌ Board filter cannot be empty")
            sys.exit(1)
    
    return board_filter


def display_filter_info(filter_data):
    """Display filter information in a formatted way"""
    print(f"📋 Filter Details:")
    print(f"   Name: {filter_data.get('name', 'N/A')}")
    print(f"   ID: {filter_data.get('id', 'N/A')}")
    print(f"   Owner: {filter_data.get('owner', {}).get('displayName', 'N/A')}")
    print(f"   Description: {filter_data.get('description', 'N/A')}")
    print(f"   JQL: {filter_data.get('jql', 'N/A')}")
    print(f"   Favourite: {filter_data.get('favourite', False)}")
    print(f"   Subscriptions: {len(filter_data.get('subscriptions', []))}")


def display_board_info(board_data):
    """Display board information in a formatted way"""
    print(f"📊 Board Details:")
    print(f"   Name: {board_data.get('name', 'N/A')}")
    print(f"   ID: {board_data.get('id', 'N/A')}")
    print(f"   Type: {board_data.get('type', 'N/A')}")
    print(f"   Self URL: {board_data.get('self', 'N/A')}")
    
    # Handle location information (project details)
    location = board_data.get('location', {})
    if location:
        print(f"   Project: {location.get('name', 'N/A')} ({location.get('key', 'N/A')})")
        print(f"   Project ID: {location.get('projectId', 'N/A')}")
    else:
        print(f"   Project: N/A")


def parse_range_input(user_input, max_num):
    """Parse user input for ranges and individual numbers
    
    Examples:
        "1-5" -> [1, 2, 3, 4, 5]
        "2,4,7" -> [2, 4, 7]  
        "1-3,6-8" -> [1, 2, 3, 6, 7, 8]
        "1,3-5,9" -> [1, 3, 4, 5, 9]
    """
    selected_indices = set()
    
    try:
        # Split by commas first
        parts = [part.strip() for part in user_input.split(',')]
        
        for part in parts:
            if '-' in part:
                # Handle range (e.g., "1-5")
                start_str, end_str = part.split('-', 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                
                if start < 1 or end > max_num or start > end:
                    return None, f"Invalid range: {part}. Must be between 1-{max_num} and start <= end"
                
                selected_indices.update(range(start, end + 1))
            else:
                # Handle individual number
                num = int(part.strip())
                if num < 1 or num > max_num:
                    return None, f"Invalid number: {num}. Must be between 1-{max_num}"
                selected_indices.add(num)
        
        return sorted(list(selected_indices)), None
        
    except ValueError as e:
        return None, f"Invalid input format. Use numbers, ranges (1-5), or comma-separated (1,3,5-7)"


def confirm_batch_deletion(filters_to_delete):
    """Prompt user to confirm batch filter deletion"""
    print(f"\n⚠️  You are about to delete {len(filters_to_delete)} filter(s):")
    print("=" * 60)
    
    for i, filter_data in enumerate(filters_to_delete, 1):
        print(f"{i:2}. 📝 {filter_data.get('name', 'N/A')} (ID: {filter_data.get('id', 'N/A')})")
        if len(filters_to_delete) <= 10:  # Show owner for smaller lists
            print(f"    👤 Owner: {filter_data.get('owner', {}).get('displayName', 'N/A')}")
    
    print("=" * 60)
    print(f"📊 Total filters to delete: {len(filters_to_delete)}")
    
    while True:
        response = input(f"\nAre you sure you want to delete these {len(filters_to_delete)} filter(s)? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def confirm_deletion(filter_name, filter_id):
    """Prompt user to confirm filter deletion"""
    print(f"\n⚠️  You are about to delete the filter:")
    print(f"   📝 Name: {filter_name}")
    print(f"   🆔 ID: {filter_id}")
    
    while True:
        response = input(f"\nAre you sure you want to delete '{filter_name}'? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def show_help():
    """Show help information about environment variables"""
    print("\n📖 HELP: Environment Variables")
    print("=" * 50)
    print("Set these environment variables to avoid prompts:")
    print("  • JIRA_URL         = https://your-company.atlassian.net")
    print("  • JIRA_USERNAME    = your-email@company.com")
    print("  • JIRA_API_TOKEN   = your-api-token")
    print("  • JIRA_BOARD_FILTER = myproject  # Required: board filter for option 4")
    print("\nExample setup:")
    print("  export JIRA_URL='https://company.atlassian.net'")
    print("  export JIRA_USERNAME='user@company.com'")
    print("  export JIRA_API_TOKEN='your-token-here'")
    print("  export JIRA_BOARD_FILTER='myproject'  # Required")
    print("  python3 delete_jira_filters.py")
    print("\n🔗 Get API token at: https://id.atlassian.com/manage-profile/security/api-tokens")


def main():
    print("🔧 JIRA Management Tool - Filters & Boards")
    print("=" * 50)
    
    # Check for help argument
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    # Show environment variable info
    print("💡 Tip: Set JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, and JIRA_BOARD_FILTER")
    print("   environment variables to customize behavior. Use --help for details.\n")
    
    # Get credentials and configuration
    try:
        jira_url, username, api_token = get_jira_credentials()
        board_filter = get_board_filter()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    
    # Initialize Jira manager (auto-detects Red Hat Jira for Bearer token auth)
    jira_manager = JiraManager(jira_url, username, api_token)
    
    print(f"\n🔗 Connected to: {jira_url}")
    
    while True:
        print(f"\n🔧 JIRA Management Options:")
        print("━" * 50)
        print("📋 FILTERS:")
        print("1. Search filters by name")
        print("2. List my filters")
        print("3. Delete filter by ID")
        print("📊 BOARDS:")
        print(f"4. Search boards containing '{board_filter.upper()}'")
        print("5. List all boards")
        print("6. Delete board by ID")
        print("━" * 50)
        print("7. Exit")
        
        try:
            choice = input("\nSelect an option (1-7): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        
        if choice == '1':
            # Search by name
            filter_name = input("Enter filter name to search for: ").strip()
            if not filter_name:
                print("❌ Filter name cannot be empty")
                continue
                
            print(f"🔍 Searching for filters matching '{filter_name}'...")
            results = jira_manager.search_filters(filter_name=filter_name)
            
            if not results:
                continue
                
            filters = results.get('values', [])
            if not filters:
                print(f"📭 No filters found matching '{filter_name}'")
                continue
                
            print(f"\n✅ Found {len(filters)} filter(s):")
            for i, filter_item in enumerate(filters, 1):
                print(f"{i:2}. {filter_item.get('name')} (ID: {filter_item.get('id')})")
                print(f"     👤 Owner: {filter_item.get('owner', {}).get('displayName', 'N/A')}")
            
            print(f"\n📋 Selection Options:")
            print(f"   • Single filter: 3")
            print(f"   • Range: 1-5")
            print(f"   • Multiple: 2,4,7")
            print(f"   • Combined: 1-3,6-8,10")
            
            try:
                selection_input = input(f"\nSelect filter(s) to delete (1-{len(filters)}): ").strip()
                if not selection_input:
                    print("❌ No selection provided")
                    continue
                
                # Parse the selection
                selected_indices, error = parse_range_input(selection_input, len(filters))
                if error:
                    print(f"❌ {error}")
                    continue
                
                # Get the selected filters
                selected_filters = [filters[i-1] for i in selected_indices]
                
                if len(selected_filters) == 1:
                    # Single filter deletion (existing behavior)
                    selected_filter = selected_filters[0]
                    details = jira_manager.get_filter_details(selected_filter['id'])
                    if details:
                        print()
                        display_filter_info(details)
                        
                        if confirm_deletion(details['name'], details['id']):
                            print(f"\n🗑️ Deleting filter '{details['name']}'...")
                            if jira_manager.delete_filter(details['id']):
                                print(f"✅ Filter '{details['name']}' deleted successfully!")
                            else:
                                print(f"❌ Failed to delete filter '{details['name']}'")
                        else:
                            print("❌ Deletion cancelled")
                else:
                    # Batch deletion
                    if confirm_batch_deletion(selected_filters):
                        print(f"\n🗑️ Deleting {len(selected_filters)} filters...")
                        successful_deletions = 0
                        failed_deletions = 0
                        
                        for filter_item in selected_filters:
                            filter_name = filter_item.get('name', 'Unknown')
                            filter_id = filter_item.get('id')
                            
                            print(f"   Deleting: {filter_name}...")
                            if jira_manager.delete_filter(filter_id):
                                successful_deletions += 1
                                print(f"   ✅ {filter_name} deleted")
                            else:
                                failed_deletions += 1
                                print(f"   ❌ Failed to delete {filter_name}")
                        
                        print(f"\n📊 Results:")
                        print(f"   ✅ Successfully deleted: {successful_deletions}")
                        if failed_deletions > 0:
                            print(f"   ❌ Failed deletions: {failed_deletions}")
                    else:
                        print("❌ Batch deletion cancelled")
                        
            except KeyboardInterrupt:
                print("❌ Operation cancelled")
                
        elif choice == '2':
            # List my filters
            print("🔍 Loading your filters...")
            filters = jira_manager.list_my_filters()
            
            if not filters:
                continue
                
            if not filters:
                print("📭 No filters found")
                continue
                
            print(f"\n📋 Your Filters ({len(filters)}):")
            for i, filter_item in enumerate(filters, 1):
                print(f"{i:2}. {filter_item.get('name')} (ID: {filter_item.get('id')})")
            
            print(f"\n📋 Selection Options:")
            print(f"   • Single filter: 3")
            print(f"   • Range: 1-5")
            print(f"   • Multiple: 2,4,7")
            print(f"   • Combined: 1-3,6-8,10")
            
            try:
                selection_input = input(f"\nSelect filter(s) to delete (1-{len(filters)}): ").strip()
                if not selection_input:
                    print("❌ No selection provided")
                    continue
                
                # Parse the selection
                selected_indices, error = parse_range_input(selection_input, len(filters))
                if error:
                    print(f"❌ {error}")
                    continue
                
                # Get the selected filters
                selected_filters = [filters[i-1] for i in selected_indices]
                
                if len(selected_filters) == 1:
                    # Single filter deletion (existing behavior)
                    selected_filter = selected_filters[0]
                    details = jira_manager.get_filter_details(selected_filter['id'])
                    if details:
                        print()
                        display_filter_info(details)
                        
                        if confirm_deletion(details['name'], details['id']):
                            print(f"\n🗑️ Deleting filter '{details['name']}'...")
                            if jira_manager.delete_filter(details['id']):
                                print(f"✅ Filter '{details['name']}' deleted successfully!")
                            else:
                                print(f"❌ Failed to delete filter '{details['name']}'")
                        else:
                            print("❌ Deletion cancelled")
                else:
                    # Batch deletion
                    if confirm_batch_deletion(selected_filters):
                        print(f"\n🗑️ Deleting {len(selected_filters)} filters...")
                        successful_deletions = 0
                        failed_deletions = 0
                        
                        for filter_item in selected_filters:
                            filter_name = filter_item.get('name', 'Unknown')
                            filter_id = filter_item.get('id')
                            
                            print(f"   Deleting: {filter_name}...")
                            if jira_manager.delete_filter(filter_id):
                                successful_deletions += 1
                                print(f"   ✅ {filter_name} deleted")
                            else:
                                failed_deletions += 1
                                print(f"   ❌ Failed to delete {filter_name}")
                        
                        print(f"\n📊 Results:")
                        print(f"   ✅ Successfully deleted: {successful_deletions}")
                        if failed_deletions > 0:
                            print(f"   ❌ Failed deletions: {failed_deletions}")
                    else:
                        print("❌ Batch deletion cancelled")
                        
            except KeyboardInterrupt:
                print("❌ Operation cancelled")
                
        elif choice == '3':
            # Delete by ID
            try:
                filter_id = input("Enter filter ID to delete: ").strip()
                if not filter_id:
                    print("❌ Filter ID cannot be empty")
                    continue
                    
                # Get filter details first
                print(f"🔍 Getting details for filter ID {filter_id}...")
                details = jira_manager.get_filter_details(filter_id)
                
                if not details:
                    print(f"❌ Filter with ID {filter_id} not found or access denied")
                    continue
                    
                print()
                display_filter_info(details)
                
                if confirm_deletion(details['name'], details['id']):
                    print(f"\n🗑️ Deleting filter '{details['name']}'...")
                    if jira_manager.delete_filter(details['id']):
                        print(f"✅ Filter '{details['name']}' deleted successfully!")
                    else:
                        print(f"❌ Failed to delete filter '{details['name']}'")
                else:
                    print("❌ Deletion cancelled")
                    
            except KeyboardInterrupt:
                print("❌ Operation cancelled")
                
        elif choice == '4':
            # Search boards using configurable filter with server-side API filtering
            print(f"🔍 Searching for boards containing '{board_filter.upper()}' (server-side filtering)...")
            
            # Use JIRA API's name parameter for server-side filtering
            results = jira_manager.search_boards(board_name=board_filter.lower())
            
            if not results:
                continue
                
            boards = results.get('values', [])
            if not boards:
                print(f"📭 No boards found containing '{board_filter.upper()}' in the name")
                continue
                
            print(f"\n✅ Found {len(boards)} board(s):")
            for i, board_item in enumerate(boards, 1):
                print(f"{i:2}. {board_item.get('name')} (ID: {board_item.get('id')})")
                print(f"     🏷️  Type: {board_item.get('type', 'N/A')}")
                location = board_item.get('location', {})
                if location:
                    print(f"     📁 Project: {location.get('name', 'N/A')} ({location.get('key', 'N/A')})")
            
            print(f"\n📋 Selection Options:")
            print(f"   • Single board: 3")
            print(f"   • Range: 1-5")
            print(f"   • Multiple: 2,4,7")
            print(f"   • Combined: 1-3,6-8,10")
            
            try:
                selection_input = input(f"\nSelect board(s) to delete (1-{len(boards)}): ").strip()
                if not selection_input:
                    print("❌ No selection provided")
                    continue
                
                # Parse the selection
                selected_indices, error = parse_range_input(selection_input, len(boards))
                if error:
                    print(f"❌ {error}")
                    continue
                
                # Get the selected boards
                selected_boards = [boards[i-1] for i in selected_indices]
                
                if len(selected_boards) == 1:
                    # Single board deletion (existing behavior)
                    selected_board = selected_boards[0]
                    details = jira_manager.get_board_details(selected_board['id'])
                    if details:
                        print()
                        display_board_info(details)
                        
                        if confirm_deletion(details['name'], details['id']):
                            print(f"\n🗑️ Deleting board '{details['name']}'...")
                            if jira_manager.delete_board(details['id']):
                                print(f"✅ Board '{details['name']}' deleted successfully!")
                            else:
                                print(f"❌ Failed to delete board '{details['name']}'")
                        else:
                            print("❌ Deletion cancelled")
                else:
                    # Batch deletion
                    if confirm_batch_deletion(selected_boards):
                        print(f"\n🗑️ Deleting {len(selected_boards)} boards...")
                        successful_deletions = 0
                        failed_deletions = 0
                        
                        for board_item in selected_boards:
                            board_name = board_item.get('name', 'Unknown')
                            board_id = board_item.get('id')
                            
                            print(f"   Deleting: {board_name}...")
                            if jira_manager.delete_board(board_id):
                                successful_deletions += 1
                                print(f"   ✅ {board_name} deleted")
                            else:
                                failed_deletions += 1
                                print(f"   ❌ Failed to delete {board_name}")
                        
                        print(f"\n📊 Results:")
                        print(f"   ✅ Successfully deleted: {successful_deletions}")
                        if failed_deletions > 0:
                            print(f"   ❌ Failed deletions: {failed_deletions}")
                    else:
                        print("❌ Batch deletion cancelled")
                        
            except KeyboardInterrupt:
                print("❌ Operation cancelled")
                
        elif choice == '5':
            # List all boards
            print("🔍 Loading all boards...")
            results = jira_manager.list_boards()
            
            if not results:
                continue
                
            boards = results.get('values', [])
            if not boards:
                print("📭 No boards found")
                continue
                
            print(f"\n📊 All Boards ({len(boards)}):")
            for i, board_item in enumerate(boards, 1):
                print(f"{i:2}. {board_item.get('name')} (ID: {board_item.get('id')})")
                print(f"     🏷️  Type: {board_item.get('type', 'N/A')}")
                location = board_item.get('location', {})
                if location:
                    print(f"     📁 Project: {location.get('name', 'N/A')} ({location.get('key', 'N/A')})")
            
            print(f"\n📋 Selection Options:")
            print(f"   • Single board: 3")
            print(f"   • Range: 1-5")
            print(f"   • Multiple: 2,4,7")
            print(f"   • Combined: 1-3,6-8,10")
            
            try:
                selection_input = input(f"\nSelect board(s) to delete (1-{len(boards)}): ").strip()
                if not selection_input:
                    print("❌ No selection provided")
                    continue
                
                # Parse the selection
                selected_indices, error = parse_range_input(selection_input, len(boards))
                if error:
                    print(f"❌ {error}")
                    continue
                
                # Get the selected boards
                selected_boards = [boards[i-1] for i in selected_indices]
                
                if len(selected_boards) == 1:
                    # Single board deletion
                    selected_board = selected_boards[0]
                    details = jira_manager.get_board_details(selected_board['id'])
                    if details:
                        print()
                        display_board_info(details)
                        
                        if confirm_deletion(details['name'], details['id']):
                            print(f"\n🗑️ Deleting board '{details['name']}'...")
                            if jira_manager.delete_board(details['id']):
                                print(f"✅ Board '{details['name']}' deleted successfully!")
                            else:
                                print(f"❌ Failed to delete board '{details['name']}'")
                        else:
                            print("❌ Deletion cancelled")
                else:
                    # Batch deletion
                    if confirm_batch_deletion(selected_boards):
                        print(f"\n🗑️ Deleting {len(selected_boards)} boards...")
                        successful_deletions = 0
                        failed_deletions = 0
                        
                        for board_item in selected_boards:
                            board_name = board_item.get('name', 'Unknown')
                            board_id = board_item.get('id')
                            
                            print(f"   Deleting: {board_name}...")
                            if jira_manager.delete_board(board_id):
                                successful_deletions += 1
                                print(f"   ✅ {board_name} deleted")
                            else:
                                failed_deletions += 1
                                print(f"   ❌ Failed to delete {board_name}")
                        
                        print(f"\n📊 Results:")
                        print(f"   ✅ Successfully deleted: {successful_deletions}")
                        if failed_deletions > 0:
                            print(f"   ❌ Failed deletions: {failed_deletions}")
                    else:
                        print("❌ Batch deletion cancelled")
                        
            except KeyboardInterrupt:
                print("❌ Operation cancelled")
                
        elif choice == '6':
            # Delete board by ID
            try:
                board_id = input("Enter board ID to delete: ").strip()
                if not board_id:
                    print("❌ Board ID cannot be empty")
                    continue
                    
                # Get board details first
                print(f"🔍 Getting details for board ID {board_id}...")
                details = jira_manager.get_board_details(board_id)
                
                if not details:
                    print(f"❌ Board with ID {board_id} not found or access denied")
                    continue
                    
                print()
                display_board_info(details)
                
                if confirm_deletion(details['name'], details['id']):
                    print(f"\n🗑️ Deleting board '{details['name']}'...")
                    if jira_manager.delete_board(details['id']):
                        print(f"✅ Board '{details['name']}' deleted successfully!")
                    else:
                        print(f"❌ Failed to delete board '{details['name']}'")
                else:
                    print("❌ Deletion cancelled")
                    
            except KeyboardInterrupt:
                print("❌ Operation cancelled")
                
        elif choice == '7':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-7.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
