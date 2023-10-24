#!/usr/bin/env bash
# script to display VPN status 
#
# to check: shellcheck -x -P $HOME/.config vpn_status.sh
set -eEuo pipefail

declare -A SSID_TO_LOCATION

# config file should set SSID_TO_LOCATION and VPN_TYPE
configFile="$HOME/.config/vpn_status" 
# shellcheck source=vpn_status
[[ -r "$configFile" ]] && source "$configFile"

VPN_TYPE="${VPN_TYPE:?VPN_TYPE must be set in $configFile}"
if [[ "$VPN_TYPE" == "ppp" ]] ; then
  VPN_DEV="${VPN_DEV:?VPN_DEV must be set in $configFile when VPN_TYPE=ppp}"
fi

location=
vpn=

function check_wifi {
  local -r wifi_intf="$(networksetup -listallhardwareports \
	  | gsed -n -e '/Wi-Fi/{ n; s/Device: //p }')"
  local -r ssid="$(networksetup -getairportnetwork "$wifi_intf" \
	  | gsed -n -e 's/^Current Wi-Fi Network: \(.*\)$/\1/p')"

  if [[ -z "$ssid" ]] ; then
    location="Offline"
  elif [[ -v 'SSID_TO_LOCATION[$ssid]' ]] ; then
    location="${SSID_TO_LOCATION[$ssid]}"
  else
    location="Internet"
  fi
}

function check_vpn {
  case "${VPN_TYPE:-ppp}" in
    ppp)
      if /usr/sbin/netstat -rn | grep -q "$VPN_DEV" ; then
        vpn=connected
      fi
      ;;
    anyconnect)
      state="$(/opt/cisco/anyconnect/bin/vpn state | grep -c 'state: Connected' || true)"
      if [[ "$state" -lt 3 ]] ; then
        # at least one component is disconnected
        vpn=
      else
        vpn=connected
      fi
      ;;
    *)
      echo "Unknown VPN_TYPE $VPN_TYPE" >&2
      ;;
  esac
}

# main
check_wifi
check_vpn

if [[ -n "$vpn" ]] ; then
  echo "On VPN"
elif [[ -n "$location" ]] ; then
  echo "$location"
else
  echo "Unknown"
fi
