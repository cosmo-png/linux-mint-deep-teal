# Deep Teal — Linux Mint Cinnamon Rice

A complete, lightweight desktop customization pack for Linux Mint Cinnamon.
Deep Teal pairs Mint's built-in dark theme with a custom matching wallpaper,
clean Bash prompt, and a few useful shell shortcuts. It needs no extra packages.

## Install

1. Download this repository as a ZIP from GitHub and extract it, or clone it.
2. Open a terminal in the extracted `linux-mint-deep-teal` folder.
3. Run:

   ```bash
   ./install.sh
   ```

4. Log out and back in (or restart Cinnamon) to refresh the desktop theme.

The installer saves a timestamped backup before editing `.bashrc`, installs
the wallpaper under `~/.local/share/wallpapers/`, and applies available Mint
theme settings. It does not install packages or change system files. If a
theme name is unavailable on your Mint version, choose a dark Mint-Y variant
in **System Settings → Themes**; the wallpaper and shell setup still work.

## What's included

- Deep teal and midnight abstract SVG wallpaper (2560 × 1440).
- Built-in Mint-Y dark GTK and Cinnamon theme settings, with Mint-Y-Aqua icons
  when installed.
- Bash prompt with the current Git branch, plus navigation, listing, and
  safer interactive file aliases.
- `mkcd` and `extract` shell helpers.
- Installer and uninstaller scripts.

## Uninstall

From the extracted folder, run:

```bash
./uninstall.sh
```

This removes the marked Bash source block, the installed shell config, and
the wallpaper, then restores the prior desktop theme settings when possible.
Backups are kept in your home directory.

## Customize

Edit `config/bashrc` for shell changes and `wallpaper/deep-teal.svg` for the
wallpaper. The source files remain untouched by installation.

## License

MIT. See [LICENSE](LICENSE).
