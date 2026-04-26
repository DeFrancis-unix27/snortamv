#!/usr/bin/env bash
set -euo pipefail

# ==============================
# COLORS
# ==============================
GREEN="\033[1;32m"
RED="\033[1;31m"
YELLOW="\033[1;33m"
RESET="\033[0m"

trap 'echo -e "${RED}Interrupted${RESET}"; exit 1' SIGINT SIGTERM
# ==============================
# CONFIGURATION
# ==============================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SNORT_PATH="/usr/sbin/snort"
RULE_PATH="$SCRIPT_DIR/rules/generated"
LOG_DIR="/var/log/snortamv"
LOG_DOC="$LOG_DIR/log_file.log"
SNORTLUA="$SCRIPT_DIR/modules/Snort_Config/linux/amv.lua"
INTERFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -n1)
RULE_FILE="$RULE_PATH/snort.rules"
DAYS_OF_VALID=7




if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root!${RESET}"
    exit 1
else
    echo -e "${GREEN}Running as root, proceeding...${RESET}"
fi

START_TIME=$(date +%s)
echo -e "${GREEN}=== SNORT AUTOMATION STARTED ===${RESET}"

# ==============================
# ASK AIM
# ==============================
echo -e "${YELLOW}[0] What is your AIM please:${RESET}"
read -r AIM

if [ -z "$AIM" ]; then
    echo -e "${RED}AIM cannot be empty${RESET}"
    exit 1
fi
# ==============================
# DETECT SNORT VERSION
# ==============================

SNORT_CONF="/etc/snort/snort.lua"



if [ ! -f "$SNORT_CONF" ]; then
    echo -e "${YELLOW}Snort config not found, generating default...${RESET}"
    sudo mkdir -p "$(dirname "$SNORT_CONF")"
    sudo cp "$SNORTLUA" "$SNORT_CONF"
    sudo chown root:root "$SNORT_CONF"
    echo -e "${GREEN}Default config created at $SNORT_CONF${RESET}"
fi


mkdir -p "$LOG_DIR"
chmod 750 "$LOG_DIR"
# ==============================
# SHOW RULES
# ==============================
echo -e "${YELLOW}RULES UPDATED:${RESET}"
if [ -d "$RULE_PATH" ]; then
    cat "$RULE_PATH"/*.rules 2>/dev/null || echo -e "${YELLOW}No .rules files found in $RULE_PATH${RESET}"
else
    echo -e "${RED}No rules found at $RULE_PATH${RESET}"
fi

# ==============================
# VALIDATE CONFIG
# ==============================
echo -e "${GREEN}[2.1] Validating Snort config...${RESET}"
if ! $SNORT_PATH -c "$SNORT_CONF" -T; then
    echo -e "${RED}Snort config validation failed${RESET}"
    exit 1
fi

# ==============================
# VALIDATE RULES   
# ==============================
echo -e "${GREEN}[2.1] Validating Snort rules...${RESET}"
if ! $SNORT_PATH -T -c "$SNORT_CONF" -R "$RULE_FILE"; then
    echo -e "${RED}Snort rules validation failed${RESET}"
    exit 1
fi

# ==============================
# View Adapters
# ==============================
if [ -z "$INTERFACE" ]; then
    echo -e "${RED}No network interface detected${RESET}"
    ip -br link show
    exit 1
else
    echo -e "${GREEN}[1.1] Available network interfaces:${RESET}"
    ip -br link show
    echo ""
    echo -e "${YELLOW}Using interface: $INTERFACE${RESET}"
fi



# ==============================
# RUN SNORT
# ==============================
echo -e "${GREEN}[3] Running Snort...${RESET}"
$SNORT_PATH -i "$INTERFACE" -c "$SNORT_CONF" -A console -l "$LOG_DIR" &
SNORT_PID=$!

sleep 10  # let it capture traffic
kill $SNORT_PID
wait $SNORT_PID 2>/dev/null || true

# ==============================
# READ ALERTS
# ==============================
ALERT_FILE="$LOG_DIR/alert_fast"
echo -e "${GREEN}[4] Reading alert logs...${RESET}"
if [ -f "$ALERT_FILE" ]; then
    cat "$ALERT_FILE"
else
 echo -e "${YELLOW}No alerts found in $ALERT_FILE${RESET}"
 ls -lh "$LOG_DIR"
fi


#==============
# LOG ACTIVITY
# ==============================
printf "%s | %s | %s\n" "$(date '+%F %T')" "$(whoami)" "$AIM" >> "$LOG_DOC"
echo -e "${YELLOW}Log documentation updated.${RESET}"
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo -e "${GREEN}Execution time: $ELAPSED seconds.${RESET}"
# ==============================
# CLEANUP OLD LOGS
# ==============================
echo -e "${GREEN}[6] Deleting logs older than $DAYS_OF_VALID days...${RESET}"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
find "$LOG_DIR" -type f -mtime +"$DAYS_OF_VALID" -exec bash -c '
  for file; do
    cp "$file" "'"$LOG_DIR"'/backup_'"$TIMESTAMP"'_$(basename "$file")
  done
' bash {} + 

find "$LOG_DIR" -type f -mtime +"$DAYS_OF_VALID" -delete

echo -e "${YELLOW}Old logs cleaned.${RESET}"

echo -e "${GREEN}=== SNORT COMPLETED SUCCESSFULLY ===${RESET}"
