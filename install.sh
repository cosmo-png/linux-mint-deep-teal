#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/deep-teal"
CONFIG_TARGET="$CONFIG_DIR/bashrc"
CONTROL_CENTER_SOURCE="$ROOT/control-center.py"
CONTROL_CENTER_TARGET="$CONFIG_DIR/control-center.py"
LOCAL_BIN="$HOME/.local/bin"
LAUNCHER="$LOCAL_BIN/deep-teal-control-center"
APPLICATIONS_DIR="$HOME/.local/share/applications"
DESKTOP_ENTRY="$APPLICATIONS_DIR/deep-teal-control-center.desktop"
BACKUP_SETTINGS="$CONFIG_DIR/desktop-settings.tsv"
WALLPAPER_DIR="$HOME/.local/share/wallpapers"
WALLPAPER_TARGET="$WALLPAPER_DIR/deep-teal.svg"
CONFIG_SOURCE="$ROOT/config/bashrc"
WALLPAPER_SOURCE="$ROOT/wallpaper/deep-teal.svg"
BASHRC="$HOME/.bashrc"
BEGIN_MARKER='# >>> deep-teal-rice >>>'
END_MARKER='# <<< deep-teal-rice <<<'

[[ -f "$CONFIG_SOURCE" ]] || CONFIG_SOURCE="$ROOT/bashrc"
[[ -f "$WALLPAPER_SOURCE" ]] || WALLPAPER_SOURCE="$ROOT/deep-teal.svg"

[[ -f "$CONFIG_SOURCE" && -f "$WALLPAPER_SOURCE" && -f "$CONTROL_CENTER_SOURCE" ]] || {
    printf 'Run this script from the extracted Deep Teal rice folder.\n' >&2
    exit 1
}

mkdir -p -- "$CONFIG_DIR" "$WALLPAPER_DIR" "$LOCAL_BIN" "$APPLICATIONS_DIR"
install -m 0644 -- "$CONFIG_SOURCE" "$CONFIG_TARGET"
install -m 0644 -- "$CONTROL_CENTER_SOURCE" "$CONTROL_CENTER_TARGET"
install -m 0644 -- "$WALLPAPER_SOURCE" "$WALLPAPER_TARGET"

cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
exec python3 "$CONTROL_CENTER_TARGET" "\$@"
EOF
chmod 0755 -- "$LAUNCHER"
escaped_app="${CONTROL_CENTER_TARGET//\\/\\\\}"
escaped_app="${escaped_app//\"/\\\"}"
cat > "$DESKTOP_ENTRY" <<EOF
[Desktop Entry]
Type=Application
Name=Deep Teal Control Center
Comment=Adjust screen brightness and audio volume
Exec=python3 "$escaped_app"
Icon=preferences-desktop
Categories=Settings;HardwareSettings;
Terminal=false
StartupNotify=true
EOF

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
printf 'Open Deep Teal Control Center from the Mint application menu.\n'
printf 'Log out and back in to refresh Cinnamon theme settings.\n'
