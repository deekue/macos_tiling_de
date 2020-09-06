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

# put skhd_parse.py in path
if [ -d "$HOME/bin" ] ; then
  ln -svi "$SRC/bin/skhd_parse.py" "$HOME/bin/skhd_parse.py"
else
  sudo ln -svi "$SRC/bin/skhd_parse.py" "/usr/local/bin/skhd_parse.py"
fi

# setup config files
[ -d "$HOME/.config" ] || mkdir -p "$HOME/.config"
for i in alacritty skhd yabai; do
  ln -svi "$SRC/config/$i" "$HOME/.config/$i"
done

# set username in Alacritty config
sed -i -e "s/USERNAME_GOES_HERE/${USER}/" "$HOME/.config/alacritty/alacritty"

# tweaks
source "${SRC}/macos"

if [ -r "${SRC}/Brewfile" ]; then 
  cd "${SRC}" && brew bundle
fi

brew services start yabai
brew services start skhd

echo "good luck!"
