# Deep Teal — Linux Mint Cinnamon Rice

A dark teal desktop setup for Linux Mint Cinnamon, with a matching wallpaper,
shell customizations, and a small control center inspired by polished Arch rice
setups. The control center offers brightness and volume sliders plus a mute
button in a compact GTK window.

## Install from GitHub

Replace `YOUR-USERNAME` with the GitHub account that hosts this repository:

```bash
git clone https://github.com/cosmo-png/linux-mint-deep-teal.git
cd linux-mint-deep-teal
chmod +x install.sh
./install.sh
```

The installer adds **Deep Teal Control Center** to the Mint application menu.
Search for that name to open the window. You can also launch it from a terminal:

```bash
deep-teal-control-center
```

Log out and back in (or restart Cinnamon) to refresh the desktop theme.

## Requirements

The control center uses Python GTK 3. Linux Mint Cinnamon normally includes the
GTK desktop libraries. If the control center reports a missing Python GTK
module, install the dependencies with:

```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 brightnessctl
```

`brightnessctl` enables the brightness slider on supported displays. The
volume slider and mute button use Mint's `pactl` audio command. Controls for
hardware that is unavailable or unsupported are disabled in the window.

## What's included

- Deep teal and midnight abstract SVG wallpaper (2560 × 1440).
- Built-in Mint-Y dark GTK and Cinnamon theme settings, with Mint-Y-Aqua icons
  when installed.
- Compact dark GTK control center for screen brightness and audio volume.
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
the control center, and `deep-teal.svg` (or `wallpaper/deep-teal.svg`) for the
wallpaper. The installer accepts either the folder layout or all files at the
repository root. Installation copies these files into your home directory and
leaves the repository unchanged.

## License

MIT. See [LICENSE](LICENSE).
