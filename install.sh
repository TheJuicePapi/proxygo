#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi

# Install required packages (adjust based on your needs)
apt-get update
apt-get install tor -y && apt-get install proxychains -y

# Install Python dependencies
# No dependencies needed

# Create symbolic link for proxygo.py
ln -s "$(pwd)/proxygo.py" /usr/local/bin/proxygo

# Clear terminal window
clear

echo "Installation complete and shortcut created! Launch a new terminal and you'll be able to run 'proxygo' from any directory!"

echo "                                                                                       "

echo "Please note that you may still need to manually edit the proxychains and torrc file in order to use proxychains. Please follow the setup instructions provided in 'README.md'"
