#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.config/deep-teal"
LAUNCHER="$HOME/.local/bin/deep-teal-control-center"
DESKTOP_ENTRY="$HOME/.local/share/applications/deep-teal-control-center.desktop"
BACKUP_SETTINGS="$CONFIG_DIR/desktop-settings.tsv"
WALLPAPER="$HOME/.local/share/wallpapers/deep-teal.svg"
BASHRC="$HOME/.bashrc"
BEGIN_MARKER='# >>> deep-teal-rice >>>'
END_MARKER='# <<< deep-teal-rice <<<'

if [[ -f "$BASHRC" ]] && grep -Fq -- "$BEGIN_MARKER" "$BASHRC"; then
    cp -p -- "$BASHRC" "$BASHRC.backup.$(date +%Y%m%d-%H%M%S)"
    tmp_file="$(mktemp "${BASHRC}.XXXXXX")"
    awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" '
        $0 == begin { skip = 1; next }
        $0 == end { skip = 0; next }
        !skip { print }
    ' "$BASHRC" > "$tmp_file"
    cat -- "$tmp_file" > "$BASHRC"
    rm -f -- "$tmp_file"
fi

if command -v gsettings >/dev/null 2>&1 && [[ -f "$BACKUP_SETTINGS" ]]; then
    while IFS=$'\t' read -r schema key value; do
        [[ -n "$schema" && -n "$key" && -n "$value" ]] || continue
        gsettings set "$schema" "$key" "$value" 2>/dev/null || true
    done < "$BACKUP_SETTINGS"
fi

rm -f -- "$WALLPAPER"
rm -f -- "$CONFIG_DIR/bashrc" "$CONFIG_DIR/control-center.py" "$CONFIG_DIR/desktop-settings.tsv"
rmdir -- "$CONFIG_DIR" 2>/dev/null || true
rm -f -- "$LAUNCHER" "$DESKTOP_ENTRY"
printf 'Deep Teal rice removed. Your .bashrc backups are kept in your home folder.\n'
