#!/usr/bin/env python3
"""Deep Teal control center for Linux Mint Cinnamon (GTK 3)."""

import re
import shutil
import subprocess

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk


CSS = b"""
window { background-color: #0d151e; color: #e8f1f3; }
.panel { background-color: #121e28; border: 1px solid #263844; border-radius: 18px; }
.title { color: #effafa; font-size: 21px; font-weight: 700; }
.subtitle { color: #8ca3ac; font-size: 12px; }
.section { color: #d9e8ea; font-size: 14px; font-weight: 600; }
.hint { color: #8ca3ac; font-size: 11px; }
scale trough { min-height: 7px; background: #263943; border-radius: 8px; }
scale highlight { background: #42d6c0; border-radius: 8px; }
scale slider { min-width: 17px; min-height: 17px; background: #d7fff6; border: 2px solid #42d6c0; border-radius: 10px; }
button { color: #e6f3f4; background: #1c3039; border: 1px solid #2b454d; border-radius: 10px; padding: 8px 12px; }
button:hover { background: #25434a; }
"""


def run(args):
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=2)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


class ControlCenter(Gtk.Window):
    def __init__(self):
        super().__init__(title="Deep Teal Control Center")
        self.set_default_size(390, 400)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(18)

        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(outer)

        heading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        title = Gtk.Label(label="Control Center", xalign=0)
        title.get_style_context().add_class("title")
        subtitle = Gtk.Label(label="Deep Teal  ·  Linux Mint Cinnamon", xalign=0)
        subtitle.get_style_context().add_class("subtitle")
        heading.pack_start(title, False, False, 0)
        heading.pack_start(subtitle, False, False, 0)
        outer.pack_start(heading, False, False, 3)

        self.brightness_slider, brightness_card, self.brightness_status = self.make_control(
            "Brightness", "display-brightness-symbolic", self.set_brightness
        )
        outer.pack_start(brightness_card, False, False, 0)
        self.volume_slider, volume_card, self.volume_status = self.make_control(
            "Volume", "audio-volume-high-symbolic", self.set_volume
        )
        outer.pack_start(volume_card, False, False, 0)

        actions = Gtk.Box(spacing=8)
        self.mute_button = Gtk.Button(label="Mute / unmute")
        self.mute_button.connect("clicked", self.toggle_mute)
        actions.pack_start(self.mute_button, True, True, 0)
        settings_button = Gtk.Button(label="Open display settings")
        settings_button.connect("clicked", lambda *_: self.launch_settings())
        actions.pack_start(settings_button, True, True, 0)
        outer.pack_start(actions, False, False, 0)

        footer = Gtk.Label(label="Changes apply immediately", xalign=0)
        footer.get_style_context().add_class("hint")
        outer.pack_start(footer, False, False, 0)

        self.available_brightness = shutil.which("brightnessctl") is not None
        self.available_audio = shutil.which("pactl") is not None
        if not self.available_brightness:
            self.brightness_slider.set_sensitive(False)
            self.brightness_status.set_text("Install brightnessctl to enable brightness control")
        if not self.available_audio:
            self.volume_slider.set_sensitive(False)
            self.volume_status.set_text("pactl audio controls are unavailable")
            self.mute_button.set_sensitive(False)

        self.refresh()
        GLib.timeout_add_seconds(2, self.refresh)

    def make_control(self, label, icon_name, callback):
        frame = Gtk.Frame()
        frame.get_style_context().add_class("panel")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)
        box.set_border_width(14)
        frame.add(box)
        top = Gtk.Box(spacing=9)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        icon.set_pixel_size(22)
        heading = Gtk.Label(label=label, xalign=0)
        heading.get_style_context().add_class("section")
        status = Gtk.Label(label="Checking…", xalign=1)
        status.get_style_context().add_class("hint")
        top.pack_start(icon, False, False, 0)
        top.pack_start(heading, True, True, 0)
        top.pack_end(status, False, False, 0)
        box.pack_start(top, False, False, 0)
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_draw_value(False)
        slider.set_hexpand(True)
        slider.connect("value-changed", callback)
        box.pack_start(slider, False, False, 0)
        return slider, frame, status

    def refresh(self):
        self._refreshing = True
        if self.available_brightness:
            current = run(["brightnessctl", "get"])
            maximum = run(["brightnessctl", "max"])
            if current and maximum and int(maximum) > 0:
                value = round(100 * int(current) / int(maximum))
                self.brightness_slider.set_value(value)
                self.brightness_status.set_text(f"{value}%")
            else:
                self.brightness_status.set_text("No backlight found")
                self.brightness_slider.set_sensitive(False)
        if self.available_audio:
            volume = run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]) or ""
            match = re.search(r"(\d+)%", volume)
            if match:
                value = min(100, int(match.group(1)))
                self.volume_slider.set_value(value)
                self.volume_status.set_text(f"{value}%")
            muted = run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"]) or ""
            self.mute_button.set_label("Unmute" if "yes" in muted else "Mute")
        self._refreshing = False
        return True

    def set_brightness(self, slider):
        if not getattr(self, "_refreshing", True) and self.available_brightness:
            value = round(slider.get_value())
            run(["brightnessctl", "set", f"{value}%"])

    def set_volume(self, slider):
        if not getattr(self, "_refreshing", True) and self.available_audio:
            value = round(slider.get_value())
            run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])

    def toggle_mute(self, *_):
        run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        self.refresh()

    def launch_settings(self):
        command = shutil.which("cinnamon-settings")
        if command:
            subprocess.Popen([command, "display"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    app = ControlCenter()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
