#!/bin/bash

# ==============================================================================
# Script: client_banned_ips.sh
# Funktion: Efficient Sync Feed -> Local F2B (sshd) & TCP/UDP Dual-Block
# ==============================================================================

# --- KONFIGURATION ---
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
FEED_URL="https://feed.sec.lemue.org/banned_ips.txt"
BAN_TIME=1209600 # 14 Tage
AUTO_UPDATE=true 
SCRIPT_URL="https://raw.githubusercontent.com/lemueIO/honey-api/main/scripts/client_banned_ips.sh"
JAIL="sshd"

# --- COLORS & AESTHETICS ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- DEPENDENCY CHECK (Fail2Ban) ---
if ! command -v fail2ban-client &>/dev/null; then
    echo -e "${YELLOW}[WARN]${NC} Fail2Ban is not installed but required."
    echo -ne "${CYAN}[PROMPT]${NC} Would you like to install fail2ban now? (y/N) [15s timeout]: "
    read -t 15 -n 1 user_input
    echo "" # Newline after input

    if [[ "$user_input" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}[INFO]${NC} Installing Fail2Ban..."
        if command -v apt-get &>/dev/null; then
            apt-get update && apt-get install -y fail2ban
        elif command -v yum &>/dev/null; then
            yum install -y fail2ban
        else
            echo -e "${RED}[ERROR]${NC} No compatible package manager found. Please install fail2ban manually."
            exit 1
        fi
        
        if ! command -v fail2ban-client &>/dev/null; then
            echo -e "${RED}[ERROR]${NC} Installation failed. Exiting."
            exit 1
        fi
        echo -e "${GREEN}[SUCCESS]${NC} Fail2Ban installed successfully."
    else
        echo -e "${RED}[ERROR]${NC} Fail2Ban is required for this script. Exiting."
        exit 1
    fi
fi

# --- BANNER ---
echo -e "${CYAN}"
echo "  _    _  ____  _   _ ______     __  _____  _____          _   _ "
echo " | |  | |/ __ \| \ | |  ____|   / / / ____|/ ____|   /\   | \ | |"
echo " | |__| | |  | |  \| | |__     / / | (___ | |       /  \  |  \| |"
echo " |  __  | |  | | . \` |  __|   / /   \___ \| |      / /\ \ | . \` |"
echo " | |  | | |__| | |\  | |____ / /    ____) | |____ / ____ \| |\  |"
echo " |_|  |_|\____/|_| \_|______/_/    |_____/ \_____/_/    \_\_| \_|"
echo -e "${NC}"
echo -e "${BLUE}[INFO]${NC} Honey-Scan Banning Client - Version 2.7.0"
echo -e "${BLUE}[INFO]${NC} Target Jail: ${YELLOW}$JAIL${NC}"
echo -e "${BLUE}[INFO]${NC} Feed URL: ${YELLOW}$FEED_URL${NC}"
echo -e "${BLUE}[INFO]${NC} Auto-Update: ${YELLOW}${AUTO_UPDATE}${NC}"
echo "----------------------------------------------------------------"

# --- SINGLETON CHECK ---
# Legacy fix: Remove old lock directory if it exists
LOCK_FILE="/var/lock/honey_client_bans.lock"
[ -d "$LOCK_FILE" ] && rm -rf "$LOCK_FILE"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo -e "${RED}[ERROR]${NC} Another instance is already running. Exiting."
    exit 1
fi

# --- AUTO UPDATE ---
self_update() {
    if [ "$AUTO_UPDATE" != "true" ]; then return; fi
    # Break loop if already restarted
    for arg in "$@"; do
        if [ "$arg" == "--restarted" ]; then return; fi
    done

    if ! command -v curl &> /dev/null || ! command -v md5sum &> /dev/null; then return; fi

    TEMP_FILE=$(mktemp)
    # Use cache-buster to avoid CDN issues
    if curl -s -f --connect-timeout 10 --retry 3 "${SCRIPT_URL}?v=$(date +%s)" -o "$TEMP_FILE"; then
        if ! bash -n "$TEMP_FILE"; then
            rm -f "$TEMP_FILE"
            return
        fi
        
        LOCAL_HASH=$(md5sum "$0" | awk '{print $1}')
        REMOTE_HASH=$(md5sum "$TEMP_FILE" | awk '{print $1}')
        
        if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
            echo -e "${YELLOW}[UPDATE]${NC} New version found. Updating..."
            cp "$TEMP_FILE" "$0"
            chmod +x "$0"
            rm -f "$TEMP_FILE"
            echo -e "${BLUE}[INFO]${NC} Honey-Scan Banning Client - Version 2.7.0"
echo -e "${BLUE}[INFO]${NC} Target Jail: ${YELLOW}$JAIL${NC}"
echo -e "${BLUE}[INFO]${NC} Feed URL: ${YELLOW}$FEED_URL${NC}"
echo -e "${BLUE}[INFO]${NC} Auto-Update: ${YELLOW}${AUTO_UPDATE}${NC}"
echo "----------------------------------------------------------------"
            exec bash "$0" "--restarted" "$@"
        fi
        rm -f "$TEMP_FILE"
    fi
}
self_update "$@"

# --- FAIL2BAN CONFIGURATION ---
echo -e "${BLUE}[INFO]${NC} Checking Fail2Ban configuration..."

NEED_RESTART=false

# 1. Custom Action Content (Idempotent Check)
ACTION_FILE="/etc/fail2ban/action.d/honey-nftables.conf"
TEMP_ACTION=$(mktemp)
cat > "$TEMP_ACTION" <<'EOF'
[Definition]
# Option:  actionstart
# Notes.:  command executed once at the start of Fail2Ban.
# Values:  CMD
#
actionstart = nft add table inet f2b-table
              nft add chain inet f2b-table f2b-chain { type filter hook input priority filter - 1\; }
              nft add set inet f2b-table addr-set-<name> { type ipv4_addr\; }
              nft add rule inet f2b-table f2b-chain ip saddr @addr-set-<name> reject

# Option:  actionstop
# Notes.:  command executed once at the end of Fail2Ban
# Values:  CMD
#
actionstop = nft delete set inet f2b-table addr-set-<name>
             # We do not flush the chain/table as other jails might use it
             # nft delete chain inet f2b-table f2b-chain

# Option:  actionban
# Notes.:  command executed when banning an IP. Take care that the
#          command is executed with Fail2Ban user rights.
# Tags:    <ip>  IP address
#          <failures>  number of failures
#          <time>  unix timestamp of the ban time
# Values:  CMD
#
actionban = nft add element inet f2b-table addr-set-<name> { <ip> }

# Option:  actionunban
# Notes.:  command executed when unbanning an IP. Take care that the
#          command is executed with Fail2Ban user rights.
# Tags:    <ip>  IP address
#          <failures>  number of failures
#          <time>  unix timestamp of the ban time
# Values:  CMD
#
actionunban = nft delete element inet f2b-table addr-set-<name> { <ip> }

[Init]
name = default
EOF

if [ ! -f "$ACTION_FILE" ] || ! cmp -s "$TEMP_ACTION" "$ACTION_FILE"; then
    echo -e "${BLUE}[INFO]${NC} Updating custom firewall action ($ACTION_FILE)..."
    mv "$TEMP_ACTION" "$ACTION_FILE"
    NEED_RESTART=true
else
    rm -f "$TEMP_ACTION"
fi

# 2. Jail Configuration Content (Idempotent Check)
OVERRIDE_CONF="/etc/fail2ban/jail.d/defaults-debian.conf"
NFT_ACTION="honey-nftables"
ACTION_SPEC="action = $NFT_ACTION"

# Extract existing whitelist if present
EXISTING_WHITELIST=$(grep -A 1 "# Hier die Whitelist einfügen:" "$OVERRIDE_CONF" 2>/dev/null | grep "^ignoreip =" | head -n 1)
if [ -z "$EXISTING_WHITELIST" ]; then
    # Fallback: Try to find any ignoreip line in the config
    EXISTING_WHITELIST=$(grep "^ignoreip =" "$OVERRIDE_CONF" 2>/dev/null | head -n 1)
fi
if [ -z "$EXISTING_WHITELIST" ]; then
    EXISTING_WHITELIST="ignoreip = 127.0.0.1/8 ::1"
fi

# Check if hfish-client action exists
if [ -f "/etc/fail2ban/action.d/hfish-client.conf" ]; then
    ACTION_SPEC="$ACTION_SPEC
         hfish-client"
fi

TEMP_CONFIG=$(mktemp)
cat > "$TEMP_CONFIG" <<EOF
[sshd]
enabled = true
# Hier die Whitelist einfügen:
$EXISTING_WHITELIST
# Redundantly set banaction to ensure Fail2Ban knows what to use for banning itself
banaction = $NFT_ACTION
# Enforce our detected action (All Ports)
$ACTION_SPEC
EOF

if [ ! -f "$OVERRIDE_CONF" ] || ! cmp -s "$TEMP_CONFIG" "$OVERRIDE_CONF"; then
    echo -e "${BLUE}[INFO]${NC} Updating Fail2Ban configuration ($OVERRIDE_CONF)..."
    mv "$TEMP_CONFIG" "$OVERRIDE_CONF"
    NEED_RESTART=true
else
    rm -f "$TEMP_CONFIG"
    echo -e "${GREEN}[OK]${NC} Configuration up to date."
fi

# 3. Ensure Service is Running
if ! fail2ban-client status "$JAIL" &>/dev/null; then
    echo -e "${YELLOW}[WARN]${NC} Jail '$JAIL' is not active. Restart required."
    NEED_RESTART=true
fi

# 4. Restart Logic
if [ "$NEED_RESTART" = true ]; then
    echo -e "${BLUE}[INFO]${NC} Configuration changed or service down. Restarting Fail2Ban..."
    service fail2ban restart &>/dev/null || systemctl restart fail2ban &>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} Fail2Ban restarted successfully."
    else
        echo -e "${YELLOW}[WARN]${NC} Service restart failed. Trying client reload..."
        fail2ban-client reload &>/dev/null
    fi
else
    echo -e "${GREEN}[OK]${NC} Fail2Ban is running and config is stable. Skipping restart."
fi

# Set Ban Time dynamically
# Note: This affects new bans.
if fail2ban-client set "$JAIL" bantime "$BAN_TIME" &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Jail '$JAIL' bantime set to ${YELLOW}$BAN_TIME${NC} seconds."
else
    echo -e "${RED}[WARN]${NC} Could not set bantime dynamically. Using jail defaults."
fi

# --- CORE LOGIC ---

# 1. Fetch Remote IPs
echo -e "${BLUE}[STEP 1/3]${NC} Fetching remote ban list..."
REMOTE_FILE=$(mktemp)
if ! curl -s -f --connect-timeout 10 --retry 3 "$FEED_URL" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' > "$REMOTE_FILE"; then
    echo -e "${RED}[ERROR]${NC} Failed to fetch feed from $FEED_URL after 3 attempts. Exiting."
    rm -f "$REMOTE_FILE"
    exit 1
fi
REMOTE_COUNT=$(wc -l < "$REMOTE_FILE")
echo -e "${GREEN}[OK]${NC} Received ${YELLOW}$REMOTE_COUNT${NC} IPs from feed."

# 2. Sync IPs to Fail2Ban
echo -e "${BLUE}[STEP 2/3]${NC} Syncing IPs to Fail2Ban jail '$JAIL'..."

# Get currently banned IPs to avoid redundant calls (Optimization)
EXISTING_BANS_FILE=$(mktemp)
fail2ban-client status "$JAIL" | grep "Banned IP list:" | sed 's/.*Banned IP list://' | tr -s ' ' '\n' | sort -u > "$EXISTING_BANS_FILE"

# Prepare IPs to ban: Remote IPs minus Existing Bans
IPS_TO_BAN_FILE=$(mktemp)
sort -u "$REMOTE_FILE" | comm -23 - "$EXISTING_BANS_FILE" > "$IPS_TO_BAN_FILE"

COUNT_TO_BAN=$(wc -l < "$IPS_TO_BAN_FILE")

if [ "$COUNT_TO_BAN" -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} No new IPs to ban. All feed IPs are already jailed."
else
    echo -e "${BLUE}[INFO]${NC} Found ${YELLOW}$COUNT_TO_BAN${NC} new IPs to ban."
    
    # Process in chunks to give feedback
    CURRENT=0
    
    while IFS= read -r ip; do
        fail2ban-client set "$JAIL" banip "$ip" &>/dev/null
        ((CURRENT++))
        
        # Progress bar every 50 IPs
        if ((CURRENT % 50 == 0)); then
             echo -ne "\r${BLUE}[INFO]${NC} Banning progress: $CURRENT / $COUNT_TO_BAN"
        fi
    done < "$IPS_TO_BAN_FILE"
    echo "" # Newline
    echo -e "${GREEN}[OK]${NC} Finished banning new IPs."
fi

rm -f "$EXISTING_BANS_FILE" "$IPS_TO_BAN_FILE" "$REMOTE_FILE"

# 3. Summary
echo -e "${BLUE}[STEP 3/3]${NC} Verification..."
TOTAL_BANS=$(fail2ban-client status "$JAIL" | grep "Currently banned:" | sed 's/.*Currently banned://' | tr -d ' ')
echo -e "${BLUE}[INFO]${NC} Total currently banned IPs in jail '$JAIL': ${YELLOW}$TOTAL_BANS${NC}"

echo "----------------------------------------------------------------"
echo -e "${GREEN}[SUCCESS]${NC} Sync completed at $(date)"
