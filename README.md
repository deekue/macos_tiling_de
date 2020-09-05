# Keyboard focused Tiling Desktop Environment for MacOS

An attempt at recreating the [i3](https://i3wm.org)/[Regolith](https://regolith-linux.org) experience on MacOS.  
Based on [skhd](https://github.com/koekeishiya/skhd) and [yabai](https://github.com/koekeishiya/yabai)

## Install
1. [Install Homebrew](https://brew.sh)
2. Clone this repo/branch  
   `git clone -b macos_tiling_wm --single-branch https://github.com/deekue/dotfiles macos_tiling_wm`
3. `cd macos_tiling_wm`
4. `bash install.sh`
5. reboot

## Usage
* The `fn` key is the base modifier.  Only tested on a MacBook, YMMV.  More bindings in progress...
* `fn + shift + ?` opens the Key Bindings window
* `fn + return` - opens the [Alacritty](https://github.com/alacritty/alacritty) terminal emulator

### Caveats / ToDos
* MacOS SIP needs to be disabled for all Yabai features to work
  * add link to Yabai doc here
  * mark affected key binds in skhdrc
  * configure Mission Control hotkeys as alternative
    * MacOS doesn't add a hotkey when a new Space is created?!
    * the plist for these hotkeys is opaque and undocumented
  * use Karabiner-Elements as alternative?
* current `fn` mapping doesn't work with external PC keyboards :(
    
