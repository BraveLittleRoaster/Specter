#!/bin/sh
set -e

# Get the IP address of eth0
IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

# Add the host entry
echo "$IP local.example.com" >> /etc/hosts

# Run the main process
exec "$@"
