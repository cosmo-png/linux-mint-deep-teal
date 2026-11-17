# Mint Shadow — Linux Mint Cinnamon Rice

A Linux Mint Cinnamon adaptation inspired by the modern settings panel and
quick controls in [DarkShadowShell](https://github.com/shadowww-dev/DarkShadowShell).
DarkShadowShell targets Hyprland and niri; this project keeps Cinnamon in
charge of the desktop and builds a separate GTK control center for Mint.

The Mint Shadow panel has Home, Appearance, Sound, Display, and About pages,
with brightness and volume sliders, mute, Mint-Y theme shortcuts, and a
wallpaper picker. It also includes a matching dark teal wallpaper and shell
customizations. This is an independent Cinnamon implementation, not the
original Quickshell code.

## Install from GitHub

Replace `YOUR-USERNAME` with the GitHub account that hosts this repository:

```bash
git clone https://github.com/cosmo-png/linux-mint-deep-teal.git
cd linux-mint-deep-teal
chmod +x install.sh
./install.sh
```

The installer adds **Mint Shadow Settings** to the Mint application menu.
Search for that name to open the window. You can also launch it from a terminal:

```bash
mint-shadow-settings
```

Log out and back in (or restart Cinnamon) to refresh the desktop theme.

## Requirements

The control center uses Python GTK 3. Linux Mint Cinnamon includes the GTK
desktop libraries. If Python GTK or brightness control is unavailable, install
these packages with:

```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 brightnessctl pulseaudio-utils
```

`brightnessctl` enables the brightness slider on supported displays. The
volume slider and mute button use Mint's `pactl` audio command. Controls for
hardware that is unavailable or unsupported are disabled in the window.

## What's included

- Deep teal and midnight abstract SVG wallpaper (2560 × 1440).
- Built-in Mint-Y dark GTK and Cinnamon theme settings, with Mint-Y-Aqua icons
  when installed.
- Mint Shadow Settings panel with quick controls, theme and wallpaper settings.
- Bash prompt with current Git branch, navigation and listing aliases, plus
  `mkcd` and `extract` helpers.
- Installer and uninstaller scripts.

The installer saves a timestamped `.bashrc` backup, records the original
desktop theme and wallpaper settings, and installs files only in your home
directory. It does not install packages or change system files. If a theme
name is unavailable on your Mint version, choose a dark Mint-Y variant in
**System Settings → Themes**; the wallpaper and shell setup still work.

## Uninstall

From the cloned repository folder, run:

```bash
./uninstall.sh
```

This removes the marked Bash source block, control center, menu launcher, and
wallpaper, then restores the saved desktop theme settings when possible.
Backups are kept in your home directory.

## Customize

Edit `bashrc` (or `config/bashrc`) for shell changes, `control-center.py` for
the settings panel, and `deep-teal.svg` (or `wallpaper/deep-teal.svg`) for the
wallpaper. The installer accepts either the folder layout or all files at the
repository root. Installation copies these files into your home directory and
leaves the repository unchanged.

## Inspiration and attribution

Mint Shadow is inspired by DarkShadowShell by shadowww-dev, distributed under
the MIT License. The original project targets Hyprland and niri; this edition
is a separate GTK/Cinnamon implementation. See [NOTICE.md](NOTICE.md) and
[DarkShadowShell](https://github.com/shadowww-dev/DarkShadowShell).

## License

MIT. See [LICENSE](LICENSE).
