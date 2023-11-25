#!/bin/bash

# this script establishes a VPN connection to dCloud

: "${VPN_SERVER:?Variable unset or empty}"
: "${VPN_USERNAME:?Variable unset or empty}"
: "${VPN_PASSWORD:?Variable unset or empty}"

run() {
    echo "$VPN_PASSWORD" | sudo openconnect "$VPN_SERVER" --passwd-on-stdin -u "$VPN_USERNAME" --no-dtls --verbose --timestamp --background -i vpn0 
}

until (run) 
do
    echo "openconnect crashed with exit code $? - respawning..." >&2
    sleep 5
done   