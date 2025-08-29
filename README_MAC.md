# JIRA MCP Tools - macOS Setup Guide

Complete setup guide for Mac users to get started with JIRA MCP Tools.

## Prerequisites

- macOS 10.14 or later
- Command Line Tools for Xcode (will be installed automatically with Homebrew)
- Admin privileges on your Mac

## Step-by-Step Setup

### 1. Install Homebrew

Homebrew is the missing package manager for macOS. If you don't have it installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**After installation**, you may need to add Homebrew to your PATH:

```bash
# For Intel Macs
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# For Apple Silicon Macs (M1/M2/M3)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Verify Homebrew is installed:
```bash
brew --version
```

### 2. Install Python via Homebrew

Install Python 3.13 (or the latest available version):

```bash
# Install specific Python version (recommended)
brew install python@3.13

# OR install the latest Python 3 (may change over time)
brew install python
```

**Note**: Using a specific version like `python@3.13` is recommended for consistency. Check available versions with:
```bash
brew search python@
```

This will install both `python3` and `pip3`. Verify the installation:

```bash
python3 --version
pip3 --version
```

If you installed a specific version, you may need to link it:
```bash
brew link python@3.13
```

### 3. Install pipx via Homebrew

pipx allows you to install Python applications in isolated environments:

```bash
brew install pipx
pipx ensurepath
```

**Important**: After installing pipx, restart your terminal or run:
```bash
source ~/.zprofile
```

Verify pipx is installed:
```bash
pipx --version
```

### 4. Install Project Dependencies

Navigate to the JIRA MCP Tools directory and install dependencies:

```bash
# If using regular pip (installs globally)
pip3 install -r requirements.txt

# OR using pipx for isolated environment (recommended)
pipx install --include-deps -r requirements.txt
```

### 5. Setup Environment Variables

Copy and customize the environment file:

```bash
cp setup_jira_env.sh.example setup_jira_env.sh
```

Edit `setup_jira_env.sh` with your favorite text editor:
```bash
# Using nano
nano setup_jira_env.sh

# Using vim
vim setup_jira_env.sh

# Using VS Code (if installed)
code setup_jira_env.sh
```

Add your JIRA credentials:
- `JIRA_URL` - Your JIRA instance URL
- `JIRA_USERNAME` - Your JIRA username/email
- `JIRA_API_TOKEN` - Your JIRA Personal Access Token

Load the environment variables:
```bash
source setup_jira_env.sh
```

### 6. Test Your Setup

Test your JIRA connection:

```bash
python3 test_redhat_jira.py
```

### 7. Use the Tools

#### Delete JIRA Filters
```bash
python3 simple_delete_jira_filters.py
```

#### Delete JIRA Boards
```bash
# List all boards
python3 simple_delete_jira_project_board.py

# Filter boards by name
python3 simple_delete_jira_project_board.py --filter "myproject"
```

## Troubleshooting

### Common Issues

**"Command not found" errors:**
- Make sure you've restarted your terminal or sourced your profile after installations
- Check that Homebrew is properly added to your PATH

**Python/pip version conflicts:**
- Use `python3` and `pip3` explicitly instead of `python` and `pip`
- Consider using `pipx` for isolated environments

**Permission errors:**
- Avoid using `sudo` with pip - use `pipx` or virtual environments instead
- If needed, use `pip3 install --user` flag

**Homebrew installation issues:**
- Ensure you have Command Line Tools: `xcode-select --install`
- Check Homebrew's official troubleshooting guide

### Getting JIRA Personal Access Token

1. Go to your JIRA instance
2. Click your profile picture → **Manage account**
3. Go to **Security** → **Create and manage API tokens**
4. Click **Create API token**
5. Give it a name and copy the generated token
6. Use this token as your `JIRA_API_TOKEN`

## Alternative: Using Virtual Environments

If you prefer using virtual environments instead of pipx:

```bash
# Create virtual environment
python3 -m venv jira-tools-env

# Activate virtual environment
source jira-tools-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# When done, deactivate
deactivate
```

## Next Steps

Once setup is complete, refer to the main [README.md](README.md) for detailed usage instructions and examples.

## Need Help?

- **Homebrew issues**: [https://brew.sh/](https://brew.sh/)
- **Python issues**: [https://www.python.org/downloads/mac-osx/](https://www.python.org/downloads/mac-osx/)
- **pipx documentation**: [https://pypa.github.io/pipx/](https://pypa.github.io/pipx/)
