#!/usr/bin/env bash
# script to display VPN status 
set -eEuo pipefail

VPN_DEV='ppp.*'

if /usr/sbin/netstat -rn | grep -q "$VPN_DEV" ; then
  echo "On VPN" 
else
  echo "Internet"
fi
