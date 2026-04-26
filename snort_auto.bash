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
RULE_FILE="$RULE_PATH/snort.rules"
LOG_DIR="/var/log/snortamv"
LOG_DOC="$LOG_DIR/log_file.log"
SNORT_CONF="/etc/snort/snort.lua"
SNORTLUA="$SCRIPT_DIR/modules/Snort_Config/linux/amv.lua"
INTERFACE=$(ip -o -4 route show to default | awk '{print $5}' | head -n1)
DAYS_OF_VALID=7

# ==============================
# ROOT CHECK
# ==============================
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root!${RESET}"
    exit 1
fi

echo -e "${GREEN}=== SNORT AUTOMATION STARTED ===${RESET}"
START_TIME=$(date +%s)

# ==============================
# CHECK SNORT
# ==============================
if [ ! -x "$SNORT_PATH" ]; then
    echo -e "${RED}Snort not found or not executable at $SNORT_PATH${RESET}"
    exit 1
fi

# ==============================
# ASK AIM
# ==============================
echo -e "${YELLOW}[0] What is your AIM?${RESET}"
read -r AIM

if [ -z "$AIM" ]; then
    echo -e "${RED}AIM cannot be empty${RESET}"
    exit 1
fi

# ==============================
# CONFIG SETUP
# ==============================
if [ ! -f "$SNORT_CONF" ]; then
    echo -e "${YELLOW}Generating default Snort config...${RESET}"
    mkdir -p "$(dirname "$SNORT_CONF")"
    cp "$SNORTLUA" "$SNORT_CONF"
    chown root:root "$SNORT_CONF"
fi

mkdir -p "$LOG_DIR"
chmod 750 "$LOG_DIR"

# ==============================
# SHOW RULES
# ==============================
echo -e "${YELLOW}RULES:${RESET}"
if [ -f "$RULE_FILE" ]; then
    cat "$RULE_FILE"
else
    echo -e "${RED}Rules file not found at $RULE_FILE${RESET}"
    exit 1
fi

# ==============================
# VALIDATE CONFIG
# ==============================
echo -e "${GREEN}Validating Snort config...${RESET}"
$SNORT_PATH -c "$SNORT_CONF" -T

# ==============================
# INTERFACE CHECK
# ==============================
if [ -z "$INTERFACE" ]; then
    echo -e "${RED}No network interface detected${RESET}"
    ip -br link show
    exit 1
fi

echo -e "${GREEN}Using interface:${RESET} $INTERFACE"

# ==============================
# RUN SNORT (10s capture)
# ==============================
echo -e "${GREEN}Running Snort...${RESET}"

$SNORT_PATH -i "$INTERFACE" -c "$SNORT_CONF" -A alert_fast -l "$LOG_DIR" &
SNORT_PID=$!

sleep 10
kill $SNORT_PID
wait $SNORT_PID 2>/dev/null || true

# ==============================
# READ ALERTS
# ==============================
ALERT_FILE="$LOG_DIR/alert_fast"

echo -e "${GREEN}Alerts:${RESET}"
if [ -f "$ALERT_FILE" ]; then
    cat "$ALERT_FILE"
else
    echo -e "${YELLOW}No alerts found${RESET}"
    ls -lh "$LOG_DIR"
fi

# ==============================
# LOG ACTIVITY
# ==============================
printf "%s | %s | %s\n" "$(date '+%F %T')" "$(whoami)" "$AIM" >> "$LOG_DOC"
echo -e "${YELLOW}Log updated${RESET}"

# ==============================
# CLEANUP OLD LOGS
# ==============================
echo -e "${GREEN}Cleaning old logs...${RESET}"

TIMESTAMP=$(date +%Y%m%d%H%M%S)

find "$LOG_DIR" -type f -mtime +"$DAYS_OF_VALID" -exec bash -c '
for file; do
  cp "$file" "'"$LOG_DIR"'/backup_'"$TIMESTAMP"'_$(basename "$file")
done
' bash {} +

find "$LOG_DIR" -type f -mtime +"$DAYS_OF_VALID" -delete

# ==============================
# DONE
# ==============================
END_TIME=$(date +%s)
echo -e "${GREEN}Execution time: $((END_TIME - START_TIME))s${RESET}"
echo -e "${GREEN}=== SNORT COMPLETED SUCCESSFULLY ===${RESET}"