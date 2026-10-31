#!/usr/bin/env python3
"""
Aegis Options — the choices screen for the Aegis installer.

Two modes:
  --install   Show all install-time options and write them to the options file
              (default /etc/calamares/aegis-options.env). The `aegis-installer`
              wrapper runs this first, then launches Calamares, which runs
              `aegis-apply` in the target to act on these choices.
  (no flag)   Runtime mode: only the options that can change on a live system
              (network mode, MAC spoofing) are editable and apply immediately
              via aegis-firewall / aegis-mac-spoof. Install-only options are shown
              disabled, for reference.

Pure GTK3 + stdlib so it runs in the minimal live image.
"""
import argparse
import os
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

OPTIONS_FILE_DEFAULT = "/etc/calamares/aegis-options.env"

NET_MODES = [
    ("tor", "Tor only — all traffic forced through Tor (fail-closed). Most anonymous."),
    ("i2p", "I2P only — i2pd proxies for .i2p services; clearnet is direct."),
    ("both", "Tor + I2P — Tor for clearnet, I2P for I2P-native services."),
    ("direct", "Direct — no forced routing. NOT anonymous (needed for pentesting)."),
]
BROWSERS = [
    ("torbrowser", "Tor Browser — strongest anti-fingerprinting (best with Tor). Not Chromium."),
    ("mullvad", "Mullvad Browser — Tor-Browser engine for non-Tor use. Not Chromium."),
    ("firefox", "Firefox ESR, hardened + uBlock/NoScript. Not Chromium."),
    ("librewolf", "LibreWolf — de-telemetried Firefox fork. Not Chromium."),
]
DESKTOPS = [
    ("xfce", "XFCE — light and fast (recommended; the 'not resource-stealing' choice)."),
    ("kde", "KDE Plasma — featureful, middleweight."),
    ("gnome", "GNOME — heaviest; not recommended for low-resource use."),
    ("i3", "i3 — minimal tiling window manager; lowest footprint."),
]
KALI_TIERS = [
    ("none", "Don't install offensive tools (recommended for a privacy daily-driver)."),
    ("kali-linux-headless", "Core Kali CLI toolset."),
    ("kali-linux-default", "Standard Kali toolset."),
    ("kali-linux-large", "Large Kali toolset (big download)."),
]
COMPARTMENTS = [
    ("sandbox", "Sandbox apps by default (firejail) — light, recommended."),
    ("vm", "VM isolation (KVM): run risky apps/a workstation Tor-only, Whonix-style. "
           "Strong but heavier; needs CPU virtualization. Not literally Qubes (no Xen)."),
    ("none", "No extra compartmentalization."),
]


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).returncode
    except Exception:  # noqa: BLE001
        return 1


class OptionsWindow(Gtk.Window):
    def __init__(self, install_mode, options_file):
        super().__init__(title="Aegis Options" + ("" if install_mode else " (runtime)"))
        self.install_mode = install_mode
        self.options_file = options_file
        self.set_default_size(620, 640)
        self.set_border_width(14)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(outer)

        title = Gtk.Label()
        title.set_markup("<big><b>Configure Aegis</b></big>")
        title.set_xalign(0)
        outer.pack_start(title, False, False, 0)

        sub = Gtk.Label()
        sub.set_markup("<small>Pick how this system should behave. You can change the "
                       "runtime options later from <b>Aegis Control</b>.</small>")
        sub.set_xalign(0); sub.set_line_wrap(True)
        outer.pack_start(sub, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        outer.pack_start(scroller, True, True, 0)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_end(8)
        scroller.add(box)

        self.net_combo = self._combo_section(
            box, "Network / anonymity mode", NET_MODES, default="tor", runtime=True)
        self.mac_switch = self._switch_section(
            box, "MAC address spoofing",
            "Randomize your hardware (MAC) address each connection. Turn OFF on "
            "captive-portal or corporate networks that bind identity to a MAC.",
            default=True, runtime=True)
        self.browser_combo = self._combo_section(
            box, "Default browser (never Chromium)", BROWSERS, default="torbrowser")
        self.de_combo = self._combo_section(
            box, "Desktop environment", DESKTOPS, default="xfce")
        self.kali_combo = self._combo_section(
            box, "Offensive toolkit (Kali)", KALI_TIERS, default="none")
        self.compartment_combo = self._combo_section(
            box, "Compartmentalization", COMPARTMENTS, default="sandbox")

        # Extra hardening toggles (install-time)
        self.stealth_switch = self._switch_section(
            box, "Stealth networking",
            "Stay quiet on the LAN: no mDNS/Avahi/LLMNR/NetBIOS, no DHCP hostname, "
            "no clearnet NTP (time synced over Tor), IPv6 off, radios off. Lowers your "
            "profile — does NOT make you invisible to a global adversary.", default=True)
        self.fde_switch = self._switch_section(
            box, "Full-disk encryption (LUKS)",
            "Encrypt the whole install. Calamares will ask for a passphrase. "
            "Strongly recommended.", default=True)
        self.persist_switch = self._switch_section(
            box, "Amnesic by default",
            "Leave no trace between sessions (browsing history etc. disabled). "
            "Encrypted persistence can still be added later.", default=True)
        self.usbguard_switch = self._switch_section(
            box, "USBGuard (block unknown USB)",
            "Require approval for new USB devices (anti-BadUSB / evil-maid).",
            default=True)
        self.ramwipe_switch = self._switch_section(
            box, "Wipe RAM on shutdown",
            "Overwrite memory at power-off to resist cold-boot attacks.",
            default=True)

        # Footer buttons
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.set_halign(Gtk.Align.END)
        cancel = Gtk.Button(label="Cancel")
        cancel.connect("clicked", lambda _b: self.destroy_quit(1))
        footer.pack_start(cancel, False, False, 0)
        ok = Gtk.Button(label="Continue to Install" if install_mode else "Apply")
        ok.get_style_context().add_class("suggested-action")
        ok.connect("clicked", self.on_ok)
        footer.pack_start(ok, False, False, 0)
        outer.pack_start(footer, False, False, 0)

        self.exit_code = 1

    # --- section builders ---
    def _header(self, box, text):
        l = Gtk.Label(); l.set_markup(f"<b>{text}</b>"); l.set_xalign(0)
        box.pack_start(l, False, False, 0)

    def _combo_section(self, box, header, items, default, runtime=False):
        self._header(box, header)
        combo = Gtk.ComboBoxText()
        for i, (key, desc) in enumerate(items):
            combo.append(key, desc)
            if key == default:
                combo.set_active(i)
        if combo.get_active() < 0:
            combo.set_active(0)
        if not self.install_mode and not runtime:
            combo.set_sensitive(False)
            combo.set_tooltip_text("Set at install time; reinstall to change.")
        box.pack_start(combo, False, False, 0)
        return combo

    def _switch_section(self, box, header, desc, default, runtime=False):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        h = Gtk.Label(); h.set_markup(f"<b>{header}</b>"); h.set_xalign(0)
        d = Gtk.Label(label=desc); d.set_xalign(0); d.set_line_wrap(True)
        d.get_style_context().add_class("dim-label")
        text.pack_start(h, False, False, 0)
        text.pack_start(d, False, False, 0)
        row.pack_start(text, True, True, 0)
        sw = Gtk.Switch(); sw.set_active(default); sw.set_valign(Gtk.Align.CENTER)
        if not self.install_mode and not runtime:
            sw.set_sensitive(False)
            sw.set_tooltip_text("Set at install time; reinstall to change.")
        row.pack_start(sw, False, False, 0)
        box.pack_start(row, False, False, 0)
        return sw

    # --- apply / write ---
    def on_ok(self, _btn):
        net = self.net_combo.get_active_id()
        mac = "yes" if self.mac_switch.get_active() else "no"
        if self.install_mode:
            self.write_options_file(net, mac)
        else:
            self.apply_runtime(net, mac)
        self.destroy_quit(0)

    def write_options_file(self, net, mac):
        lines = [
            "# Written by aegis_options.py --install; consumed by aegis-apply.",
            f"AEGIS_NETMODE={net}",
            f"AEGIS_MAC_SPOOF={mac}",
            f"AEGIS_BROWSER={self.browser_combo.get_active_id()}",
            f"AEGIS_DE={self.de_combo.get_active_id()}",
            f"AEGIS_KALI={self.kali_combo.get_active_id()}",
            f"AEGIS_COMPARTMENT={self.compartment_combo.get_active_id()}",
            f"AEGIS_STEALTH={'yes' if self.stealth_switch.get_active() else 'no'}",
            f"AEGIS_FDE={'yes' if self.fde_switch.get_active() else 'no'}",
            f"AEGIS_AMNESIC={'yes' if self.persist_switch.get_active() else 'no'}",
            f"AEGIS_USBGUARD={'yes' if self.usbguard_switch.get_active() else 'no'}",
            f"AEGIS_RAM_WIPE={'yes' if self.ramwipe_switch.get_active() else 'no'}",
        ]
        try:
            os.makedirs(os.path.dirname(self.options_file), exist_ok=True)
            with open(self.options_file, "w") as f:
                f.write("\n".join(lines) + "\n")
        except PermissionError:
            # Need root to write into /etc/calamares; re-exec via pkexec.
            tmp = "/tmp/aegis-options.env"
            with open(tmp, "w") as f:
                f.write("\n".join(lines) + "\n")
            sh(["pkexec", "install", "-D", "-m0644", tmp, self.options_file])

    def apply_runtime(self, net, mac):
        # Flip live toggles immediately.
        sh(["pkexec", "sh", "-c",
            f"echo {net} > /etc/aegis/netmode && /usr/local/bin/aegis-firewall {net}"])
        sh(["pkexec", "/usr/local/bin/aegis-mac-spoof", "on" if mac == "yes" else "off"])

    def destroy_quit(self, code):
        self.exit_code = code
        self.destroy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true",
                    help="installer mode: write the options file for aegis-apply")
    ap.add_argument("--firstrun", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--options-file", default=OPTIONS_FILE_DEFAULT)
    args = ap.parse_args()

    win = OptionsWindow(install_mode=args.install, options_file=args.options_file)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    sys.exit(getattr(win, "exit_code", 1))


if __name__ == "__main__":
    main()
