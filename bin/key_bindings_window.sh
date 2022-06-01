#!/usr/bin/env bash
#
# launch Key Bindings window and style/position it

set -eEuo pipefail

WindowTitle="Key Bindings"
WindowGrid="3:6:3:1:1:1"
CacheFile="$HOME/.cache/skhd/skhd.html"
SkhdConfig="$HOME/.config/skhd/skhdrc"

function generateCache {
  if [[ "$CacheFile" -ot "$SkhdConfig" ]] ; then
    $HOME/bin/skhd_parse.py \
      --format html \
      --output "$CacheFile" \
      --config "$SkhdConfig"
  fi
}

function getWindowId {
  yabai -m query --windows \
    | jq ".[] | select(.app == \"Google Chrome\") | select(.title == \"${WindowTitle}\") | .id"
}

function openWindow {
  open -na "Google Chrome" --args \
    --new-window \
    --name="${WindowTitle}" \
    --app="file://${CacheFile}"
}

function positionWindow {
  local -r windowId="${1:?arg1 is windowId}"
  yabai -m window ${windowId} --toggle float
  yabai -m window ${windowId} --toggle sticky  # may require SIP?
  yabai -m window ${windowId} --toggle topmost
  yabai -m window ${windowId} --grid "${WindowGrid}"
  yabai -m window ${windowId} --focus
}

function waitForWindowId {
  local windowId

  for i in $(seq 1 10) ; do
    windowId="$(getWindowId)"
    if [[ -n "${windowId}" ]] ; then
      break
    fi
    sleep 0.5
  done
  echo "${windowId}"
}

function closeWindow {
  local -r windowId="${1:?arg1 is windowId}"

  yabai -m window "${windowId}" --close
}

generateCache
windowId="$(getWindowId)"
if [[ -z "${windowId}" ]] ; then
  openWindow
  windowId="$(waitForWindowId)"
  positionWindow "$windowId"
else
  closeWindow "${windowId}"
fi
