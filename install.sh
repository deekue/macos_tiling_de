#!/usr/bin/env bash
#
# QaD installer

set -eEuo pipefail

SRC="$( cd -P "$(dirname -- "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd )"

# check if SIP is enabled
if command -v csrutil 2> /dev/null; then
  csrutil status
  # TODO if enabled show link to Yabai SIP doc
fi

# put scripts in path
for script in $SRC/bin/* ; do
  script_name="$(basename "$script")"
  if [ -d "$HOME/bin" ] ; then
    ln -svi "$script" "$HOME/bin/$script_name"
  else
    sudo ln -svi "$script" "/usr/local/bin/$script_name"
  fi
done

# dir for output of skhd_parse.py
[ -d "$HOME/.cache/skhd" ] || mkdir -p "$HOME/.cache/skhd"

# setup config files
[ -d "$HOME/.config" ] || mkdir -p "$HOME/.config"
for i in alacritty skhd yabai; do
  ln -svi -t "$HOME/.config" "$SRC/config/$i"
done

# set username in Alacritty config
sed -i '.bak' -e "s/USERNAME_GOES_HERE/${USER}/" "$HOME/.config/alacritty/alacritty.yml"

# tweaks
source "${SRC}/macos"

if [ -r "${SRC}/Brewfile" ]; then 
  cd "${SRC}" && brew bundle
fi

brew services start yabai
brew services start skhd
brew services start spacebar

echo "good luck!"
