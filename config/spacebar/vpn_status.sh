#!/usr/bin/env bash
# script to display VPN status 
set -eEuo pipefail

if /usr/sbin/netstat -rn | grep -q utun2 ; then
  echo "On VPN" 
else
  echo "Internet"
fi
