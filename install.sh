#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/deep-teal"
CONFIG_TARGET="$CONFIG_DIR/bashrc"
BACKUP_SETTINGS="$CONFIG_DIR/desktop-settings.tsv"
WALLPAPER_DIR="$HOME/.local/share/wallpapers"
WALLPAPER_TARGET="$WALLPAPER_DIR/deep-teal.svg"
BASHRC="$HOME/.bashrc"
BEGIN_MARKER='# >>> deep-teal-rice >>>'
END_MARKER='# <<< deep-teal-rice <<<'

[[ -f "$ROOT/config/bashrc" && -f "$ROOT/wallpaper/deep-teal.svg" ]] || {
    printf 'Run this script from the extracted Deep Teal rice folder.\n' >&2
    exit 1
}

mkdir -p -- "$CONFIG_DIR" "$WALLPAPER_DIR"
install -m 0644 -- "$ROOT/config/bashrc" "$CONFIG_TARGET"
install -m 0644 -- "$ROOT/wallpaper/deep-teal.svg" "$WALLPAPER_TARGET"

if [[ ! -e "$BASHRC" ]]; then touch -- "$BASHRC"; fi
if ! grep -Fq -- "$BEGIN_MARKER" "$BASHRC"; then
    cp -p -- "$BASHRC" "$BASHRC.backup.$(date +%Y%m%d-%H%M%S)"
    {
        printf '\n%s\n' "$BEGIN_MARKER"
        printf '[ -r "$HOME/.config/deep-teal/bashrc" ] && source "$HOME/.config/deep-teal/bashrc"\n'
        printf '%s\n' "$END_MARKER"
    } >> "$BASHRC"
fi

if command -v gsettings >/dev/null 2>&1; then
    schemas="$(gsettings list-schemas)"
    if [[ ! -f "$BACKUP_SETTINGS" ]]; then
        : > "$BACKUP_SETTINGS"
        for spec in 'org.cinnamon.desktop.interface gtk-theme' 'org.cinnamon.desktop.interface icon-theme' 'org.cinnamon.theme name' 'org.cinnamon.desktop.background picture-uri' 'org.cinnamon.desktop.background picture-options'; do
            schema="${spec% *}"; key="${spec##* }"
            if grep -Fxq -- "$schema" <<< "$schemas" && gsettings list-keys "$schema" | grep -Fxq -- "$key"; then
                value="$(gsettings get "$schema" "$key" 2>/dev/null || true)"
                [[ -n "$value" ]] && printf '%s\t%s\t%s\n' "$schema" "$key" "$value" >> "$BACKUP_SETTINGS"
            fi
        done
    fi
    set_setting() {
        local schema="$1" key="$2" value="$3"
        if grep -Fxq -- "$schema" <<< "$schemas" && gsettings list-keys "$schema" | grep -Fxq -- "$key"; then
            gsettings set "$schema" "$key" "$value" 2>/dev/null || true
        fi
    }
    set_setting org.cinnamon.desktop.interface gtk-theme "Mint-Y-Dark"
    set_setting org.cinnamon.desktop.interface icon-theme "Mint-Y-Aqua"
    set_setting org.cinnamon.theme name "Mint-Y-Dark"
    set_setting org.cinnamon.desktop.background picture-uri "file://$WALLPAPER_TARGET"
    set_setting org.cinnamon.desktop.background picture-options "zoom"
else
    printf 'gsettings was not found; apply the wallpaper and theme in System Settings.\n'
fi

printf 'Deep Teal rice installed. Open a new terminal to load the shell prompt.\n'
printf 'Wallpaper: %s\n' "$WALLPAPER_TARGET"
printf 'Log out and back in to refresh Cinnamon theme settings.\n'
