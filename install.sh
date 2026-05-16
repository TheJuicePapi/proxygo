#!/bin/bash
set -euo pipefail

# Check if running as root
if [ "${EUID}" -ne 0 ]; then
    echo "Please run as root: sudo ./install.sh"
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This installer currently supports apt-based Linux distributions."
    echo "Install tor, proxychains4, and python3 manually, then symlink proxygo.py."
    exit 1
fi

apt-get update
apt-get install -y tor proxychains4 python3

install -m 0755 "$(pwd)/proxygo.py" /usr/local/bin/proxygo

# Create the default user config for the invoking sudo user when possible.
TARGET_USER="${SUDO_USER:-}"
if [ -n "${TARGET_USER}" ] && [ "${TARGET_USER}" != "root" ]; then
    sudo -u "${TARGET_USER}" /usr/local/bin/proxygo init-config >/dev/null
else
    /usr/local/bin/proxygo init-config >/dev/null
fi

clear 2>/dev/null || true
cat <<'MSG'
ProxyGo installation complete!

Launch the advanced menu with:
  proxygo

Useful commands:
  proxygo status
  proxygo run
  proxygo generate-config

ProxyGo now keeps its own configuration under ~/.config/proxygo/ and launches
proxychains with the generated config file for better control.
MSG
