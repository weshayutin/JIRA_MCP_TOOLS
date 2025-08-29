#!/usr/bin/env python3
"""
Simple JIRA Board Management Tool

A clean, easy-to-read script for listing and deleting JIRA project boards.
Focus on core functionality with minimal complexity.

ENVIRONMENT VARIABLES:
    JIRA_URL            - Your JIRA instance URL (e.g., https://issues.redhat.com)
    JIRA_USERNAME       - Your JIRA username or email 
    JIRA_API_TOKEN      - Your JIRA API token or Personal Access Token
    JIRA_BOARD_FILTER   - Filter for board names (optional, can use --filter flag instead)

USAGE:
    python3 simple_delete_jira_project_board.py [--filter FILTER_NAME]
    python3 simple_delete_jira_project_board.py -f FILTER_NAME

EXAMPLES:
    # Using environment variable
    export JIRA_URL="https://issues.redhat.com"
    export JIRA_USERNAME="your-email@redhat.com"
    export JIRA_API_TOKEN="your-personal-access-token"
    export JIRA_BOARD_FILTER="myproject"
    python3 simple_delete_jira_project_board.py

    # Using command line flag
    python3 simple_delete_jira_project_board.py --filter "myproject"
    python3 simple_delete_jira_project_board.py -f "dev-team"

NOTE: 
    - Board filter searches for boards containing the specified text (case-insensitive)
    - Without a filter, all accessible boards will be listed
    - Only delete boards you have permission to delete and that you're sure about
"""

import requests
import os
import sys
import argparse


class SimpleJiraBoardManager:
    """Simple JIRA manager focused on board operations"""
    
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
    
    def get_all_boards(self):
        """Get all boards accessible to the current user"""
        url = f"{self.jira_url}/rest/agile/1.0/board"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('values', [])
        except requests.exceptions.RequestException as e:
            print(f"Error getting boards: {e}")
            return None
    
    def search_boards(self, board_filter=None):
        """Search for boards by name filter"""
        url = f"{self.jira_url}/rest/agile/1.0/board"
        params = {}
        
        if board_filter:
            params['name'] = board_filter.lower()
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('values', [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching boards: {e}")
            return None
    
    def get_board_details(self, board_id):
        """Get detailed information about a board"""
        url = f"{self.jira_url}/rest/agile/1.0/board/{board_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting board details for {board_id}: {e}")
            return None
    
    def delete_board(self, board_id):
        """Delete a board by ID"""
        url = f"{self.jira_url}/rest/agile/1.0/board/{board_id}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting board {board_id}: {e}")
            return False


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Simple JIRA Board Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --filter "myproject"          # Filter boards containing 'myproject'
  %(prog)s -f "dev-team"                # Filter boards containing 'dev-team'  
  %(prog)s                              # List all accessible boards (if no JIRA_BOARD_FILTER set)
        """)
    
    parser.add_argument(
        '-f', '--filter',
        help='Filter boards by name (searches for boards containing this text)'
    )
    
    return parser.parse_args()


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
        print("export JIRA_BOARD_FILTER='myproject'  # Optional")
        sys.exit(1)
    
    return jira_url, username, api_token


def get_board_filter(args):
    """Get board filter from command line args or environment variable"""
    # Command line flag takes precedence
    if args.filter:
        return args.filter
    
    # Fall back to environment variable
    board_filter = os.getenv('JIRA_BOARD_FILTER')
    
    return board_filter  # Can be None


def display_boards(boards, board_filter=None):
    """Display boards in a numbered list"""
    if board_filter:
        print(f"\nFiltered JIRA Boards containing '{board_filter}' ({len(boards)}):")
    else:
        print(f"\nAll Accessible JIRA Boards ({len(boards)}):")
    print("-" * 80)
    
    for i, board_item in enumerate(boards, 1):
        name = board_item.get('name', 'Unknown')
        board_id = board_item.get('id', 'Unknown')
        board_type = board_item.get('type', 'Unknown')
        
        # Get project information
        location = board_item.get('location', {})
        project_name = location.get('name', 'Unknown')
        project_key = location.get('key', 'Unknown')
        
        print(f"{i:2}. {name}")
        print(f"    ID: {board_id} | Type: {board_type}")
        print(f"    Project: {project_name} ({project_key})")
    
    print("-" * 80)


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


def confirm_deletion(boards_to_delete):
    """Ask user to confirm deletion"""
    count = len(boards_to_delete)
    
    print(f"\nYou are about to delete {count} board(s):")
    for board_item in boards_to_delete:
        name = board_item.get('name', 'Unknown')
        board_id = board_item.get('id', 'Unknown')
        board_type = board_item.get('type', 'Unknown')
        location = board_item.get('location', {})
        project = location.get('name', 'Unknown')
        
        print(f"  - {name} (ID: {board_id}, Type: {board_type}, Project: {project})")
    
    print(f"\n⚠️  WARNING: Deleting boards will permanently remove them from JIRA!")
    print(f"⚠️  Make sure you have permission to delete these boards.")
    
    while True:
        response = input(f"\nDelete these {count} board(s)? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def main():
    """Main function - simple and clean"""
    print("Simple JIRA Board Management Tool")
    print("=" * 40)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Get credentials and filter
    jira_url, username, api_token = get_credentials()
    board_filter = get_board_filter(args)
    jira = SimpleJiraBoardManager(jira_url, username, api_token)
    
    print(f"Connected to: {jira_url}")
    
    if board_filter:
        print(f"Board filter: '{board_filter}'")
    
    # Get and display boards
    if board_filter:
        print(f"\nSearching for boards containing '{board_filter}'...")
        boards = jira.search_boards(board_filter)
    else:
        print("\nLoading all accessible boards...")
        boards = jira.get_all_boards()
    
    if boards is None:
        print("Error occurred while fetching boards.")
        sys.exit(1)
    
    if len(boards) == 0:
        if board_filter:
            print(f"No boards found containing '{board_filter}'.")
        else:
            print("No boards found or you don't have access to any boards.")
        sys.exit(0)
    
    display_boards(boards, board_filter)
    
    # Get user selection
    print("\nSelection examples:")
    print("  Single: 3")
    print("  Range: 1-5") 
    print("  Multiple: 2,4,7")
    print("  Combined: 1-3,6-8")
    print("  All: 1-" + str(len(boards)))
    
    try:
        selection = input(f"\nSelect boards to delete (1-{len(boards)}): ").strip()
        if not selection:
            print("No selection made. Exiting.")
            sys.exit(0)
        
        # Parse selection
        indices, error = parse_selection(selection, len(boards))
        if error:
            print(f"Error: {error}")
            sys.exit(1)
        
        # Get selected boards
        selected_boards = [boards[i-1] for i in indices]
        
        # Confirm deletion
        if not confirm_deletion(selected_boards):
            print("Deletion cancelled.")
            sys.exit(0)
        
        # Delete boards
        print(f"\nDeleting {len(selected_boards)} board(s)...")
        
        successful = 0
        failed = 0
        
        for board_item in selected_boards:
            name = board_item.get('name', 'Unknown')
            board_id = board_item.get('id')
            
            print(f"  Deleting '{name}'... ", end='')
            if jira.delete_board(board_id):
                print("✓")
                successful += 1
            else:
                print("✗")
                failed += 1
        
        # Summary
        print(f"\nResults: {successful} deleted, {failed} failed")
        
        if failed > 0:
            print("\nNote: Some boards may have failed to delete due to:")
            print("  - Insufficient permissions")
            print("  - Board dependencies (active sprints, etc.)")
            print("  - Board protection settings")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
