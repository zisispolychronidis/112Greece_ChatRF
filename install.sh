#!/bin/bash

# 112 Greece Alerts Module - Installation Script
# Cross-platform: Linux, macOS, Windows (Git Bash/WSL/Cygwin)
#
# WINDOWS USERS:
#   Run this script in Git Bash (comes with Git for Windows)
#   Download Git for Windows: https://git-scm.com/download/win
#   Then right-click in folder → "Git Bash Here" → run: ./install.sh /path/to/ChatRF
#
# LINUX/MAC USERS:
#   Run: ./install.sh /path/to/ChatRF

set -e

echo "🚨 112 Greece Emergency Alerts Module - Installation"
echo "===================================================="
echo ""

# Detect operating system
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
elif grep -qi microsoft /proc/version 2>/dev/null; then
    OS="wsl"
fi

echo "Detected OS: $OS"
echo ""

# Check if ChatRF directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/ChatRF"
    echo ""
    if [ "$OS" = "windows" ]; then
        echo "Example (Git Bash): $0 /c/Users/YourName/ChatRF"
        echo "Example (relative):  $0 ../ChatRF"
    else
        echo "Example: $0 ~/ChatRF"
    fi
    exit 1
fi

CHATRF_DIR="$1"

# Convert Windows paths if needed (for Git Bash)
if [ "$OS" = "windows" ]; then
    # Convert backslashes to forward slashes
    CHATRF_DIR="${CHATRF_DIR//\\//}"
fi

# Validate ChatRF directory
if [ ! -d "$CHATRF_DIR" ]; then
    echo "❌ Error: Directory not found: $CHATRF_DIR"
    exit 1
fi

if [ ! -d "$CHATRF_DIR/modules" ]; then
    echo "❌ Error: modules/ directory not found in $CHATRF_DIR"
    echo "   Are you sure this is a ChatRF installation?"
    exit 1
fi

echo "✅ Found ChatRF installation at: $CHATRF_DIR"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."

# Determine python/pip command
PYTHON_CMD="python3"
PIP_CMD="pip3"

if [ "$OS" = "windows" ]; then
    # On Windows, try python before python3
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    fi
else
    # On Linux/Mac, prefer python3
    if ! command -v python3 &> /dev/null && command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    fi
fi

echo "Using Python: $PYTHON_CMD"
$PIP_CMD install twscrape
echo "✅ Dependencies installed"
echo ""

# Copy module file
echo "📁 Installing module..."
cp service_112greece_alerts.py "$CHATRF_DIR/modules/"
echo "✅ Module installed to: $CHATRF_DIR/modules/service_112greece_alerts.py"
echo ""

# Create data directory if it doesn't exist
if [ ! -d "$CHATRF_DIR/data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p "$CHATRF_DIR/data"
    echo "✅ Data directory created"
    echo ""
fi

# Check if config exists and add configuration
CONFIG_FILE="$CHATRF_DIR/config/settings/config.ini"
if [ -f "$CONFIG_FILE" ]; then
    echo "⚙️  Configuration file found: $CONFIG_FILE"
    
    # Check if [112Greece] section already exists
    if grep -q "^\[112Greece\]" "$CONFIG_FILE"; then
        echo "⚠️  [112Greece] section already exists in config.ini"
        echo "   Skipping automatic configuration to avoid duplicates"
        echo "   Please verify your configuration manually"
    else
        echo "📝 Adding [112Greece] configuration to config.ini..."
        
        # Create backup
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        echo "   Created backup: $CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Add configuration
        echo "" >> "$CONFIG_FILE"
        cat config_snippet.ini >> "$CONFIG_FILE"
        
        echo "✅ Configuration added successfully!"
        echo ""
        echo "📋 Default configuration added:"
        echo "   - check_interval: 300 seconds (5 minutes)"
        echo "   - announcement_prefix: Προσοχή! Νέα ειδοποίηση από το 112"
        echo "   - filter_regions: (empty - announces all alerts)"
        echo ""
        echo "💡 To filter by region, edit $CONFIG_FILE"
        echo "   and set filter_regions = Βορείου_Αιγαίου (or your region)"
    fi
    echo ""
else
    echo "⚠️  Warning: config.ini not found at expected location"
    echo "   Please manually add the configuration from config_snippet.ini"
    echo ""
fi

# Detect terminal emulator and open twscrape setup in new terminal
echo "🔧 Opening new terminal for twscrape setup..."
echo ""

# Create a setup script for the new terminal
SETUP_SCRIPT=$(mktemp)

# Export CHATRF_DIR so the setup script can use it
export CHATRF_DIR

cat > "$SETUP_SCRIPT" << 'TWSCRAPE_EOF'
#!/bin/bash

echo "================================================"
echo "   twscrape Setup for 112 Greece Alerts"
echo "================================================"
echo ""
echo "You need to add a Twitter account to twscrape."
echo ""
echo "⚠️  IMPORTANT: For security, consider creating"
echo "   a dedicated Twitter account just for scraping."
echo ""
echo "You will need:"
echo "  - Twitter username"
echo "  - Twitter password"
echo "  - Email address (linked to Twitter account)"
echo "  - Email password (see note below!)"
echo ""
echo "🔐 ABOUT EMAIL PASSWORD:"
echo "   This is the password for your EMAIL account,"
echo "   NOT your Twitter password."
echo ""
echo "   ⚠️  USE APP-SPECIFIC PASSWORDS (NOT main password):"
echo "   - Gmail: https://myaccount.google.com/apppasswords"
echo "   - Outlook: Account Security → App passwords"
echo "   - Yahoo: Account Security → App password"
echo ""
echo "   🛡️  BEST PRACTICE:"
echo "   Create a NEW email + Twitter account just for this:"
echo "   - Email: my112bot@gmail.com"
echo "   - Twitter: @my112scraper"
echo "   - Use app-specific password for the email"
echo ""
read -p "Press Enter to continue..."
echo ""

# Determine ChatRF directory from script location or ask user
CHATRF_DIR="${CHATRF_DIR:-$PWD}"
DATA_DIR="$CHATRF_DIR/data/112greece"

# Create data directory if it doesn't exist
echo "📁 Setting up data directory..."
mkdir -p "$DATA_DIR"
echo "   Database location: $DATA_DIR/accounts.db"
echo ""

# Add account
echo "📝 Adding Twitter account to twscrape..."
echo ""
echo "Format: username:password:email:email_password"
echo "Example: my112bot:mypass123:bot@example.com:emailapppass456"
echo ""
read -p "Enter account details: " ACCOUNT_DETAILS

if [ ! -z "$ACCOUNT_DETAILS" ]; then
    cd "$DATA_DIR" || exit 1

    # Write credentials to file for twscrape
    ACCOUNT_FILE="account.txt"
    echo "$ACCOUNT_DETAILS" > "$ACCOUNT_FILE"

    echo ""
    echo "➕ Adding account via twscrape..."
    twscrape add_accounts "./$ACCOUNT_FILE" username:password:email:email_password

    echo ""
    echo "🔐 Logging in to Twitter account..."
    twscrape login_accounts

    echo ""
    echo "✅ twscrape setup complete!"
    echo ""
    echo "📊 Database created at: $DATA_DIR/accounts.db"
else
    echo ""
    echo "⚠️  No account details provided."
    echo "   You can set up twscrape manually later:"
    echo ""
    echo "   cd $DATA_DIR"
    echo "   echo \"username:password:email:email_password\" > account.txt"
    echo "   twscrape add_accounts ./account.txt"
    echo "   twscrape login_accounts"
fi

echo ""
read -p "Press Enter to close this terminal..."
TWSCRAPE_EOF

chmod +x "$SETUP_SCRIPT"

# Try different terminal emulators based on OS
TERMINAL_OPENED=false

if [ "$OS" = "windows" ]; then
    # Windows (Git Bash/MSYS2/Cygwin)
    
    # Convert the setup script path to Windows format for commands that need it
    SETUP_SCRIPT_WIN=$(cygpath -w "$SETUP_SCRIPT" 2>/dev/null || echo "$SETUP_SCRIPT")
    
    # Method 1: Try to launch git-bash.exe directly (most reliable for Git Bash users)
    GIT_BASH_EXE=""
    for path in "/c/Program Files/Git/git-bash.exe" "/c/Program Files (x86)/Git/git-bash.exe" "$PROGRAMFILES/Git/git-bash.exe"; do
        if [ -f "$path" ]; then
            GIT_BASH_EXE="$path"
            break
        fi
    done
    
    if [ -n "$GIT_BASH_EXE" ]; then
        # Launch new Git Bash window with the setup script
        "$GIT_BASH_EXE" -c "bash '$SETUP_SCRIPT'; echo ''; read -p 'Press Enter to close...'" &
        TERMINAL_OPENED=true
        
    # Method 2: Use Windows 'start' command via cmd
    elif command -v cmd.exe &> /dev/null; then
        # Create a wrapper batch file to launch bash
        BATCH_WRAPPER=$(mktemp --suffix=.bat)
        cat > "$BATCH_WRAPPER" << BAT_EOF
@echo off
bash.exe "$SETUP_SCRIPT"
pause
BAT_EOF
        BATCH_WRAPPER_WIN=$(cygpath -w "$BATCH_WRAPPER" 2>/dev/null || echo "$BATCH_WRAPPER")
        cmd.exe /c start "twscrape Setup" "$BATCH_WRAPPER_WIN" &
        TERMINAL_OPENED=true
        
    # Method 3: Try Windows Terminal
    elif command -v wt.exe &> /dev/null; then
        wt.exe bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
        
    # Method 4: Try mintty
    elif command -v mintty &> /dev/null; then
        mintty -e bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    fi
    
elif [ "$OS" = "wsl" ]; then
    # WSL - try to launch Windows Terminal or fall back to Linux terminals
    
    if command -v wt.exe &> /dev/null; then
        wt.exe bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    elif command -v cmd.exe &> /dev/null; then
        cmd.exe /c start "twscrape Setup" bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    # Fall back to Linux terminal emulators
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal -e "bash '$SETUP_SCRIPT'" &
        TERMINAL_OPENED=true
    fi
    
elif [ "$OS" = "linux" ] || [ "$OS" = "macos" ]; then
    # Linux/macOS terminals
    
    # Try gnome-terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    # Try xfce4-terminal
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal -e "bash '$SETUP_SCRIPT'" &
        TERMINAL_OPENED=true
    # Try konsole
    elif command -v konsole &> /dev/null; then
        konsole -e bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    # Try macOS Terminal.app
    elif command -v osascript &> /dev/null && [ "$OS" = "macos" ]; then
        osascript -e "tell application \"Terminal\" to do script \"bash '$SETUP_SCRIPT'\""
        TERMINAL_OPENED=true
    # Try xterm
    elif command -v xterm &> /dev/null; then
        xterm -e bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    # Try mate-terminal
    elif command -v mate-terminal &> /dev/null; then
        mate-terminal -e "bash '$SETUP_SCRIPT'" &
        TERMINAL_OPENED=true
    # Try terminology
    elif command -v terminology &> /dev/null; then
        terminology -e bash "$SETUP_SCRIPT" &
        TERMINAL_OPENED=true
    fi
fi

if [ "$TERMINAL_OPENED" = true ]; then
    echo "✅ Opened new terminal for twscrape setup"
    echo "   Follow the instructions in the new terminal window"
    echo ""
else
    echo "⚠️  Could not detect terminal emulator"
    echo "   Please set up twscrape manually:"
    echo ""
    echo "   twscrape add_accounts USERNAME PASSWORD EMAIL EMAIL_PASSWORD"
    echo "   twscrape login_accounts"
    echo ""
    
    # Offer to run setup in current terminal
    echo "Would you like to run the setup in this terminal instead? (y/n)"
    read -r RESPONSE
    if [[ "$RESPONSE" =~ ^[Yy]$ ]]; then
        bash "$SETUP_SCRIPT"
    fi
fi

# Instructions
echo "📋 Next Steps:"
echo ""
echo "1. ✅ Module installed"
echo "2. ✅ Dependencies installed"
echo "3. ✅ Configuration added to config.ini"
echo "4. ⏳ Complete twscrape setup in the new terminal"
echo "5. 🔄 Restart ChatRF"
echo "6. 📊 Check logs: tail -f $CHATRF_DIR/logs/repeater.log | grep '112 Greece'"
echo ""

echo "✨ Installation complete!"
echo ""
echo "For more information, see README.md"
echo ""
