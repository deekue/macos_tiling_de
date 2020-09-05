#!/bin/sh

set -eEuo pipefail

SRC="$(pwd)"

[ -r "Brewfile" ] && brew bundle || exit 1
if [ -d "$HOME/bin" ] ; then
  ln -svi "$SRC/bin/skhd_parse.py" "$HOME/bin/skhd_parse.py"
else
  sudo ln -svi "$SRC/bin/skhd_parse.py" "/usr/local/bin/skhd_parse.py"
fi
[ -d "$HOME/.config" ] || mkdir -p "$HOME/.config"
for i in alacritty skhd yabai; do
  ln -svi "$SRC/config/$i" "$HOME/.config/$i"
done

# set username in Alacritty config
sed -i -e "s/USERNAME_GOES_HERE/${USER}/" "$HOME/.config/alacritty/alacritty"

# tweaks
bash "${SRC}/macos"

brew services start yabai
brew services start skhd

echo "good luck!"
