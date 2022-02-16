# Keyboard focused Tiling Desktop Environment for MacOS

An attempt at recreating the [i3](https://i3wm.org)/[Regolith](https://regolith-linux.org) experience on MacOS.  
Based on [skhd](https://github.com/koekeishiya/skhd), [yabai](https://github.com/koekeishiya/yabai), and [spacebar](https://github.com/cmacrae/spacebar).

## Install
1. [Install Homebrew](https://brew.sh)
2. Clone this repo
   `git clone https://github.com/deekue/macos_tiling_de`
3. `cd macos_tiling_de`
4. `bash install.sh`
5. reboot

## Usage
* The `fn` key is the base modifier.  Only tested on a MacBook, YMMV.  More bindings in progress...
* `fn + shift + ?` opens the [Key Bindings window](https://github.com/deekue/macos_tiling_de/blob/master/keybindings_window-thumb.png?raw=true)
* `fn + return` - opens the [Alacritty](https://github.com/alacritty/alacritty) terminal emulator
* `fn + shift + return` - opens the [Google Chrome](https://google.com/chrome/) web browser

### Caveats / ToDos
* MacOS SIP needs to be disabled for some Yabai features to work
  * see Yabai doc [Disabling System Integrity Protection](https://github.com/koekeishiya/yabai/wiki/Disabling-System-Integrity-Protection)
  * TODO mark affected key binds in [skhdrc](blob/master/config/skhd/skhdrc)
  * configure Mission Control hotkeys as alternative?
    * MacOS doesn't add a hotkey when a new Space is created?!
    * the plist for these hotkeys is opaque and undocumented
* current `fn` mapping doesn't work with external PC keyboards :(
  * use [Karabiner-Elements](https://karabiner-elements.pqrs.org/) to map a key to `fn`
    
