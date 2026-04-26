#!/usr/bin/env bash
set -euo pipefail

# ==============================
# PATHS
# ==============================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK_DIR="$SCRIPT_DIR/lock"
SSLKEYLOGFILE="$LOCK_DIR/ssl.log.txt"

LOG_DIR="/var/log/snortamv"
OUT_DIR="/tmp/snort_decrypt"

mkdir -p "$LOCK_DIR" "$OUT_DIR"

# ==============================
# COLORS
# ==============================
GREEN="\033[1;32m"
RED="\033[1;31m"
YELLOW="\033[1;33m"
RESET="\033[0m"

# ==============================
# PREPARE KEY FILE
# ==============================
if [ ! -f "$SSLKEYLOGFILE" ]; then
    touch "$SSLKEYLOGFILE"
    chmod 600 "$SSLKEYLOGFILE"
fi

echo -e "${GREEN}=== TLS DECRYPTION TOOL ===${RESET}"
echo "Key log file: $SSLKEYLOGFILE"
echo

# ==============================
# DEPENDENCY CHECK
# ==============================
if ! command -v tshark >/dev/null 2>&1; then
    echo -e "${RED}tshark not found. Install with:${RESET}"
    echo "sudo apt install wireshark"
    exit 1
fi

if ! command -v text2pcap >/dev/null 2>&1; then
    echo -e "${YELLOW}text2pcap not found (optional)${RESET}"
fi

# ==============================
# CHECK TLS KEYS
# ==============================
if [ ! -s "$SSLKEYLOGFILE" ]; then
    echo -e "${YELLOW}TLS key file is empty.${RESET}"
    echo "Run this first:"
    echo "export SSLKEYLOGFILE=\"$SSLKEYLOGFILE\""
    echo "Then open browser and visit HTTPS sites."
    read -rp "Press ENTER after generating traffic..."
fi

if [ ! -s "$SSLKEYLOGFILE" ]; then
    echo -e "${RED}Still no TLS keys found.${RESET}"
    exit 1
fi

echo -e "${GREEN}TLS keys detected.${RESET}"

# ==============================
# SELECT FILE
# ==============================
echo
echo "Available log files:"
ls -lh "$LOG_DIR"
echo

read -rp "Enter filename (PCAP preferred): " filename
FILEPATH="$LOG_DIR/$filename"

if [ ! -f "$FILEPATH" ]; then
    echo -e "${RED}File not found${RESET}"
    exit 1
fi

# ==============================
# DETECT FILE TYPE
# ==============================
FILETYPE=$(file "$FILEPATH")
echo "Detected type: $FILETYPE"

PCAP="$OUT_DIR/output.pcap"

if echo "$FILETYPE" | grep -qi "pcap"; then
    echo -e "${GREEN}Using existing PCAP${RESET}"
    PCAP="$FILEPATH"
else
    echo -e "${YELLOW}WARNING: Non-PCAP input detected${RESET}"
    echo "Attempting reconstruction (may FAIL for TLS)"

    HEXFILE="$OUT_DIR/hex.txt"

    sed -nE 's/^[[:space:]]*[0-9A-Fa-f]{4}[[:space:]]+//p' "$FILEPATH" \
        | sed -E 's/[[:space:]]{2,}.*$//' > "$HEXFILE"

    text2pcap -l 1 "$HEXFILE" "$PCAP"
fi

# ==============================
# DECRYPT
# ==============================
echo
echo -e "${GREEN}Decrypting traffic...${RESET}"

tshark \
  -o tls.keylog_file:"$SSLKEYLOGFILE" \
  -r "$PCAP" \
  -Y "tls || http" \
  -V | head -n 200

# ==============================
# OPTIONAL: CLEAN HTTP VIEW
# ==============================
echo
echo -e "${GREEN}Extracting HTTP (if decrypted):${RESET}"

tshark \
  -o tls.keylog_file:"$SSLKEYLOGFILE" \
  -r "$PCAP" \
  -Y http \
  -T fields \
  -e ip.src -e ip.dst -e http.host -e http.request.uri

# ==============================
# DONE
# ==============================
echo
echo -e "${GREEN}=== DONE ===${RESET}"
echo "PCAP: $PCAP"
echo "KEYS: $SSLKEYLOGFILE"