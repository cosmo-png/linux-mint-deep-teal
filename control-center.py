#!/usr/bin/env python3
"""Mint Shadow: a Cinnamon-native quick settings and appearance center."""

import re
import shutil
import subprocess

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk


CSS = b"""
window { background: #0d141b; color: #edf4f4; }
.rail { background: #101a22; border-right: 1px solid #23343b; }
.brand { color: #dbfff6; font-size: 19px; font-weight: 700; }
.muted { color: #91a6ad; font-size: 12px; }
.page-title { color: #eefafa; font-size: 25px; font-weight: 700; }
.section-title { color: #def2f1; font-size: 15px; font-weight: 650; }
.card { background: #14212a; border: 1px solid #263b43; border-radius: 18px; }
.nav-button { background: transparent; border: 0; border-radius: 12px; color: #a8bbc0; padding: 10px 12px; text-align: left; }
.nav-button:hover { background: #1a2b33; color: #edffff; }
.nav-active { background: #203b3c; color: #8af0d6; }
button { color: #eaf8f6; background: #1a3037; border: 1px solid #2a484c; border-radius: 11px; padding: 9px 13px; }
button:hover { background: #244449; }
button.accent { color: #071714; background: #70e5c7; border-color: #70e5c7; font-weight: 650; }
entry { color: #eaf8f6; background: #132129; border: 1px solid #2c4148; border-radius: 10px; padding: 9px; }
scale trough { min-height: 7px; background: #2a4045; border-radius: 8px; }
scale highlight { background: #70e5c7; border-radius: 8px; }
scale slider { min-width: 17px; min-height: 17px; background: #e0fff6; border: 2px solid #55cbb1; border-radius: 10px; }
"""


def command(args):
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=2)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


class MintShadow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mint Shadow Settings")
        self.set_default_size(980, 680)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(0)
        self._refreshing = True
        self.brightness_scales = []
        self.volume_scales = []

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        layout = Gtk.Box()
        self.add(layout)
        rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rail.set_size_request(205, -1)
        rail.set_border_width(18)
        rail.get_style_context().add_class("rail")
        layout.pack_start(rail, False, False, 0)

        brand = Gtk.Label(label="Mint Shadow", xalign=0)
        brand.get_style_context().add_class("brand")
        rail.pack_start(brand, False, False, 3)
        brand_sub = Gtk.Label(label="DESKTOP SETTINGS", xalign=0)
        brand_sub.get_style_context().add_class("muted")
        rail.pack_start(brand_sub, False, False, 12)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE, transition_duration=140)
        self.page_titles = {}
        self.nav_buttons = {}
        for key, label, icon in [
            ("home", "Home", "go-home-symbolic"),
            ("appearance", "Appearance", "preferences-desktop-theme-symbolic"),
            ("sound", "Sound", "audio-volume-high-symbolic"),
            ("display", "Display", "video-display-symbolic"),
            ("about", "About", "help-about-symbolic"),
        ]:
            button = Gtk.Button()
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.get_style_context().add_class("nav-button")
            row = Gtk.Box(spacing=11)
            icon_widget = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            row.pack_start(icon_widget, False, False, 0)
            row.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
            button.add(row)
            button.connect("clicked", self.show_page, key)
            rail.pack_start(button, False, False, 0)
            self.nav_buttons[key] = button

        spacer = Gtk.Box()
        rail.pack_end(spacer, True, True, 0)
        foot = Gtk.Label(label="CINNAMON EDITION  •  1.0", xalign=0)
        foot.get_style_context().add_class("muted")
        rail.pack_end(foot, False, False, 4)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_border_width(26)
        layout.pack_start(content, True, True, 0)
        top = Gtk.Box(spacing=14)
        self.header = Gtk.Label(label="Home", xalign=0)
        self.header.get_style_context().add_class("page-title")
        top.pack_start(self.header, True, True, 0)
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search settings")
        self.search.set_size_request(230, -1)
        self.search.connect("search-changed", self.search_changed)
        top.pack_end(self.search, False, False, 0)
        content.pack_start(top, False, False, 0)
        content.pack_start(self.stack, True, True, 0)

        self.stack.add_named(self.build_home(), "home")
        self.stack.add_named(self.build_appearance(), "appearance")
        self.stack.add_named(self.build_sound(), "sound")
        self.stack.add_named(self.build_display(), "display")
        self.stack.add_named(self.build_about(), "about")
        self.show_page(None, "home")
        self.refresh()
        GLib.timeout_add_seconds(3, self.refresh)

    def card(self, title, subtitle=None):
        frame = Gtk.Frame()
        frame.get_style_context().add_class("card")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(18)
        frame.add(box)
        heading = Gtk.Label(label=title, xalign=0)
        heading.get_style_context().add_class("section-title")
        box.pack_start(heading, False, False, 0)
        if subtitle:
            hint = Gtk.Label(label=subtitle, xalign=0, wrap=True)
            hint.get_style_context().add_class("muted")
            box.pack_start(hint, False, False, 0)
        return frame, box

    def scale_control(self, box, title, callback, collection):
        row = Gtk.Box(spacing=12)
        label = Gtk.Label(label=title, xalign=0)
        label.set_size_request(90, -1)
        row.pack_start(label, False, False, 0)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_draw_value(True)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.set_hexpand(True)
        scale.connect("value-changed", callback)
        row.pack_start(scale, True, True, 0)
        box.pack_start(row, False, False, 0)
        collection.append(scale)
        return scale

    def build_home(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        intro = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        welcome = Gtk.Label(label="Your desktop, your way.", xalign=0)
        welcome.get_style_context().add_class("section-title")
        desc = Gtk.Label(label="Quick controls and a calmer Cinnamon setup.", xalign=0)
        desc.get_style_context().add_class("muted")
        intro.pack_start(welcome, False, False, 0)
        intro.pack_start(desc, False, False, 0)
        page.pack_start(intro, False, False, 4)

        brightness_card, brightness_box = self.card(
            "Brightness", "Adjust the built-in display backlight"
        )
        self.brightness_status = Gtk.Label(label="Looking for a backlight…", xalign=0)
        self.brightness_status.get_style_context().add_class("muted")
        brightness_box.pack_start(self.brightness_status, False, False, 0)
        self.scale_control(brightness_box, "Level", self.set_brightness, self.brightness_scales)
        page.pack_start(brightness_card, False, False, 0)

        audio_card, audio_box = self.card("Sound", "Control your default output device")
        self.audio_status = Gtk.Label(label="Checking audio…", xalign=0)
        self.audio_status.get_style_context().add_class("muted")
        audio_box.pack_start(self.audio_status, False, False, 0)
        self.scale_control(audio_box, "Volume", self.set_volume, self.volume_scales)
        audio_actions = Gtk.Box(spacing=9)
        self.mute_button = Gtk.Button(label="Mute")
        self.mute_button.connect("clicked", self.toggle_mute)
        audio_actions.pack_start(self.mute_button, False, False, 0)
        open_sound = Gtk.Button(label="Sound settings")
        open_sound.connect("clicked", lambda *_: self.launch_settings("sound"))
        audio_actions.pack_start(open_sound, False, False, 0)
        audio_box.pack_start(audio_actions, False, False, 0)
        page.pack_start(audio_card, False, False, 0)

        open_appearance = Gtk.Button(label="Personalize appearance")
        open_appearance.get_style_context().add_class("accent")
        open_appearance.connect("clicked", lambda *_: self.show_page(None, "appearance"))
        page.pack_start(open_appearance, False, False, 0)
        return page

    def build_appearance(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        theme_card, theme_box = self.card("Theme", "Switch between the built-in Mint-Y looks")
        theme_buttons = Gtk.Box(spacing=10)
        dark = Gtk.Button(label="Dark")
        dark.connect("clicked", lambda *_: self.set_theme(True))
        light = Gtk.Button(label="Light")
        light.connect("clicked", lambda *_: self.set_theme(False))
        theme_buttons.pack_start(dark, False, False, 0)
        theme_buttons.pack_start(light, False, False, 0)
        theme_box.pack_start(theme_buttons, False, False, 0)
        self.theme_status = Gtk.Label(label="Mint-Y theme controls", xalign=0)
        self.theme_status.get_style_context().add_class("muted")
        theme_box.pack_start(self.theme_status, False, False, 0)
        page.pack_start(theme_card, False, False, 0)

        wallpaper_card, wallpaper_box = self.card(
            "Wallpaper", "Choose an image to set as your Cinnamon desktop background"
        )
        choose = Gtk.Button(label="Choose wallpaper…")
        choose.get_style_context().add_class("accent")
        choose.connect("clicked", self.choose_wallpaper)
        wallpaper_box.pack_start(choose, False, False, 0)
        page.pack_start(wallpaper_card, False, False, 0)

        note = Gtk.Label(
            label="Mint Shadow keeps Cinnamon in charge of your panel, windows, and desktop session.",
            xalign=0,
            wrap=True,
        )
        note.get_style_context().add_class("muted")
        page.pack_start(note, False, False, 3)
        return page

    def build_sound(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        card, box = self.card("Audio output", "Volume changes apply immediately")
        self.sound_status = Gtk.Label(label="Checking audio service…", xalign=0)
        self.sound_status.get_style_context().add_class("muted")
        box.pack_start(self.sound_status, False, False, 0)
        self.scale_control(box, "Volume", self.set_volume, self.volume_scales)
        buttons = Gtk.Box(spacing=10)
        mute = Gtk.Button(label="Mute / unmute")
        mute.connect("clicked", self.toggle_mute)
        buttons.pack_start(mute, False, False, 0)
        settings = Gtk.Button(label="Open Sound settings")
        settings.connect("clicked", lambda *_: self.launch_settings("sound"))
        buttons.pack_start(settings, False, False, 0)
        box.pack_start(buttons, False, False, 0)
        page.pack_start(card, False, False, 0)
        return page

    def build_display(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        card, box = self.card("Display settings", "Cinnamon provides monitor layout and resolution controls")
        open_button = Gtk.Button(label="Open Display settings")
        open_button.get_style_context().add_class("accent")
        open_button.connect("clicked", lambda *_: self.launch_settings("display"))
        box.pack_start(open_button, False, False, 0)
        page.pack_start(card, False, False, 0)

        brightness_card, brightness_box = self.card("Screen brightness", "Laptop backlight control")
        self.display_brightness_status = Gtk.Label(label="See Home for the brightness slider", xalign=0)
        self.display_brightness_status.get_style_context().add_class("muted")
        brightness_box.pack_start(self.display_brightness_status, False, False, 0)
        page.pack_start(brightness_card, False, False, 0)
        return page

    def build_about(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        card, box = self.card("Mint Shadow", "A community desktop customization for Linux Mint Cinnamon")
        desc = Gtk.Label(
            label=("A Mint-native take on a modern rice: quick controls, theme shortcuts, "
                   "and a clean settings panel that works alongside Cinnamon."),
            xalign=0,
            wrap=True,
        )
        box.pack_start(desc, False, False, 0)
        credit = Gtk.Label(
            label="Design inspiration: DarkShadowShell by shadowww-dev (MIT). This Cinnamon app is a separate implementation.",
            xalign=0,
            wrap=True,
        )
        credit.get_style_context().add_class("muted")
        box.pack_start(credit, False, False, 0)
        page.pack_start(card, False, False, 0)
        return page

    def show_page(self, _button, name):
        self.stack.set_visible_child_name(name)
        self.header.set_text(name.title())
        for key, button in self.nav_buttons.items():
            context = button.get_style_context()
            if key == name:
                context.add_class("nav-active")
            else:
                context.remove_class("nav-active")

    def search_changed(self, entry):
        query = entry.get_text().strip().lower()
        if not query:
            return
        for key, label in [("home", "home brightness volume"),
                           ("appearance", "appearance theme wallpaper"),
                           ("sound", "sound audio volume mute"),
                           ("display", "display screen brightness monitor"),
                           ("about", "about version credit")]:
            if query in label:
                self.show_page(None, key)
                return

    def refresh(self):
        self._refreshing = True
        if shutil.which("brightnessctl"):
            current = command(["brightnessctl", "get"])
            maximum = command(["brightnessctl", "max"])
            try:
                value = min(100, round(100 * int(current) / int(maximum))) if current and maximum else None
            except (ValueError, ZeroDivisionError):
                value = None
            if value is not None:
                for scale in self.brightness_scales:
                    scale.set_value(value)
                self.brightness_status.set_text(f"Backlight available · {value}%")
                self.display_brightness_status.set_text(f"Backlight available · {value}%")
            else:
                self.brightness_status.set_text("No supported backlight found; install brightnessctl to enable")
                self.display_brightness_status.set_text("No supported backlight found")
        else:
            self.brightness_status.set_text("Install brightnessctl to enable brightness control")
            self.display_brightness_status.set_text("Install brightnessctl to enable brightness control")

        if shutil.which("pactl"):
            raw = command(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]) or ""
            match = re.search(r"(\d+)%", raw)
            if match:
                value = min(100, int(match.group(1)))
                for scale in self.volume_scales:
                    scale.set_value(value)
                self.audio_status.set_text(f"Default output · {value}%")
                self.sound_status.set_text(f"Default output · {value}%")
            mute = command(["pactl", "get-sink-mute", "@DEFAULT_SINK@"]) or ""
            self.mute_button.set_label("Unmute" if "yes" in mute else "Mute")
        else:
            self.audio_status.set_text("pactl audio controls are unavailable")
            self.sound_status.set_text("Install pulseaudio-utils for audio controls")
            self.mute_button.set_sensitive(False)
        self._refreshing = False
        return True

    def set_brightness(self, scale):
        if not self._refreshing and shutil.which("brightnessctl"):
            command(["brightnessctl", "set", f"{round(scale.get_value())}%"])

    def set_volume(self, scale):
        if not self._refreshing and shutil.which("pactl"):
            command(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{round(scale.get_value())}%"])

    def toggle_mute(self, *_):
        command(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        self.refresh()

    def set_theme(self, dark):
        gtk_theme = "Mint-Y-Dark" if dark else "Mint-Y"
        icon_theme = "Mint-Y-Aqua" if dark else "Mint-Y"
        success = self.set_gsetting("org.cinnamon.desktop.interface", "gtk-theme", gtk_theme)
        success &= self.set_gsetting("org.cinnamon.desktop.interface", "icon-theme", icon_theme)
        success &= self.set_gsetting("org.cinnamon.theme", "name", gtk_theme)
        self.theme_status.set_text("Theme changed" if success else "Some theme settings were unavailable on this Mint version")

    @staticmethod
    def set_gsetting(schema, key, value):
        if not shutil.which("gsettings"):
            return False
        keys = command(["gsettings", "list-keys", schema])
        if not keys or key not in keys.splitlines():
            return False
        try:
            subprocess.run(["gsettings", "set", schema, key, value], check=True, timeout=3)
            return True
        except (OSError, subprocess.SubprocessError):
            return False

    def choose_wallpaper(self, *_):
        dialog = Gtk.FileChooserDialog(
            title="Choose wallpaper",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Choose", Gtk.ResponseType.ACCEPT)
        image_filter = Gtk.FileFilter()
        image_filter.set_name("Images")
        for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.svg"):
            image_filter.add_pattern(pattern)
        dialog.add_filter(image_filter)
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            uri = dialog.get_uri()
            self.set_gsetting("org.cinnamon.desktop.background", "picture-uri", uri)
            self.set_gsetting("org.cinnamon.desktop.background", "picture-uri-dark", uri)
        dialog.destroy()

    @staticmethod
    def launch_settings(section):
        binary = shutil.which("cinnamon-settings")
        if binary:
            subprocess.Popen([binary, section], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    window = MintShadow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
