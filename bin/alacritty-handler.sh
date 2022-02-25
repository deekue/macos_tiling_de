#!/usr/bin/env bash
#
# Wrapper to open files in a terminal
#
# TODO add support for all possible options in Terminal's plist
# /usr/libexec/PlistBuddy -c Print /System/Applications/Utilities/Terminal.app/Contents/Info.plist
#
# TODO can you detect a "role" from this script, if so can handle URLs and extensions
# TODO can Automator handle menu options?
# TODO edit the plist for this "app", add relevant entries from Terminal's plist
# TODO refactor to use functions so user's rc file can override
# TODO package app?

[[ -r "$HOME/.handlerrc" ]] && source "$HOME/.handlerrc"
BIN="/Applications/Alacritty.app/Contents/MacOS/alacritty"

# defaults
FALLBACK_BIN="/Applications/Utilities/Terminal.app/Contents/MacOS/Terminal"
BIN="${BIN:-$FALLBACK_BIN}"

case "$1" in
  ssh:*)
    "$BIN" -e ssh "${1#ssh://}"
    ;;
  telnet:*)
    "$BIN" -e telnet "${1#telnet://}"
    ;;
  x-man-page:*)
    "$BIN" -e man "${1#x-man-page://}"
    ;;
  *://*)
    # unsupported URL scheme, punt
    open "$@"
    ;;
  *)
    echo "$@"
    ;;
esac
