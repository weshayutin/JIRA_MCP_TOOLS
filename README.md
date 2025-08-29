# JIRA MCP Tools

Simple command-line tools for managing JIRA filters and boards.

## Quick Start

### 1. Setup Environment Variables

Copy the example environment file and customize it with your JIRA credentials:

```bash
cp setup_jira_env.sh.example setup_jira_env.sh
```

Edit `setup_jira_env.sh` and add your JIRA credentials:
- `JIRA_URL` - Your JIRA instance URL (e.g., `https://issues.redhat.com`)
- `JIRA_USERNAME` - Your JIRA username or email
- `JIRA_API_TOKEN` - Your JIRA Personal Access Token

Then source the environment file:
```bash
source setup_jira_env.sh
```

### 2. Test Your Authentication

Verify your JIRA connection works:

```bash
python3 test_redhat_jira.py
```

This will test different authentication methods and confirm your credentials are working.

### 3. Use the Tools

#### Delete JIRA Filters
List and delete your JIRA filters using range selection:

```bash
python3 simple_delete_jira_filters.py
```

#### Delete JIRA Boards  
List and delete JIRA boards with optional filtering:

```bash
# List all accessible boards
python3 simple_delete_jira_project_board.py

# Filter boards by name
python3 simple_delete_jira_project_board.py --filter "myproject"

# Or use environment variable
export JIRA_BOARD_FILTER="dev-team"
python3 simple_delete_jira_project_board.py
```

## Range Selection Examples

Both tools support flexible range selection:
- Single item: `3`
- Range: `1-5` (items 1 through 5)
- Multiple: `2,4,7` (items 2, 4, and 7)
- Combined: `1-3,6-8,10` (items 1-3, 6-8, and 10)

## Requirements

- Python 3.x
- `requests` library: `pip install requests`
- JIRA Personal Access Token (get from your JIRA profile settings)

## Notes

- Scripts auto-detect Red Hat JIRA vs standard JIRA authentication
- All operations require confirmation before deletion
- Only delete items you own or have permission to delete
