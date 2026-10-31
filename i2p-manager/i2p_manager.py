#!/usr/bin/env python3
"""
Aegis I2P Manager — a lightweight GTK front-end for the i2pd router.

Does NOT reimplement I2P. It drives the system `i2pd` service and reads live
stats from the i2pd web console (http://127.0.0.1:7070), so it stays tiny and
"non-resource-stealing" — the whole point of using i2pd over the Java router.

Privileged actions (start/stop/restart) go through pkexec so the GUI runs as a
normal user. Read-only stats need no privilege.
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import re
import subprocess
import urllib.request

CONSOLE_URL = "http://127.0.0.1:7070/"
TUNNELS_CONF = "/etc/i2pd/tunnels.conf"
SERVICE = "i2pd"
REFRESH_MS = 3000


def run(cmd):
    """Run a command, return (rc, stdout+stderr)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def service_active():
    rc, _ = run(["systemctl", "is-active", "--quiet", SERVICE])
    return rc == 0


def svc_action(action):
    # pkexec prompts for the admin password via PolicyKit.
    return run(["pkexec", "systemctl", action, SERVICE])


def fetch_console_stats():
    """Scrape a few headline numbers from the i2pd console main page."""
    stats = {"uptime": "—", "received": "—", "sent": "—",
             "routers": "—", "client_tunnels": "—", "status": "—"}
    try:
        with urllib.request.urlopen(CONSOLE_URL, timeout=4) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None  # console unreachable (i2pd down or still starting)

    text = re.sub(r"<[^>]+>", " ", html)      # strip tags
    text = re.sub(r"\s+", " ", text)

    def grab(label, default="—"):
        m = re.search(re.escape(label) + r"\s*:?\s*([^A-Z<]{1,40}?)(?=[A-Z][a-z]|$)", text)
        return m.group(1).strip() if m else default

    stats["uptime"] = grab("Uptime")
    stats["status"] = grab("Network status") or grab("Status")
    stats["received"] = grab("Received")
    stats["sent"] = grab("Sent")
    stats["routers"] = grab("Routers")
    stats["client_tunnels"] = grab("Client Tunnels") or grab("Tunnels")
    return stats


class I2PManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Aegis — I2P Manager")
        self.set_default_size(460, 420)
        self.set_border_width(12)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(12); root.set_margin_bottom(12)
        root.set_margin_start(12); root.set_margin_end(12)
        self.add(root)

        # Header: status pill + toggle
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.status_lbl = Gtk.Label(label="Checking…")
        self.status_lbl.set_xalign(0)
        header.pack_start(self.status_lbl, True, True, 0)

        self.toggle_btn = Gtk.Button(label="Start I2P")
        self.toggle_btn.connect("clicked", self.on_toggle)
        header.pack_end(self.toggle_btn, False, False, 0)

        restart = Gtk.Button(label="Restart")
        restart.connect("clicked", self.on_restart)
        header.pack_end(restart, False, False, 0)
        root.pack_start(header, False, False, 0)

        root.pack_start(Gtk.Separator(), False, False, 0)

        # Live stats grid
        grid = Gtk.Grid(column_spacing=14, row_spacing=8)
        self.fields = {}
        rows = [("Network status", "status"), ("Uptime", "uptime"),
                ("Data received", "received"), ("Data sent", "sent"),
                ("Known routers", "routers"), ("Client tunnels", "client_tunnels")]
        for i, (label, key) in enumerate(rows):
            l = Gtk.Label(label=label + ":"); l.set_xalign(0)
            l.get_style_context().add_class("dim-label")
            v = Gtk.Label(label="—"); v.set_xalign(0); v.set_selectable(True)
            grid.attach(l, 0, i, 1, 1)
            grid.attach(v, 1, i, 1, 1)
            self.fields[key] = v
        root.pack_start(grid, False, False, 0)

        root.pack_start(Gtk.Separator(), False, False, 0)

        # Actions
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        console_btn = Gtk.Button(label="Open Router Console")
        console_btn.connect("clicked", lambda _b: self.open_url(CONSOLE_URL))
        actions.pack_start(console_btn, True, True, 0)

        tunnels_btn = Gtk.Button(label="Edit Tunnels…")
        tunnels_btn.connect("clicked", self.on_edit_tunnels)
        actions.pack_start(tunnels_btn, True, True, 0)
        root.pack_start(actions, False, False, 0)

        # Proxy hint
        hint = Gtk.Label()
        hint.set_markup(
            "<small>Browser proxy for .i2p sites: HTTP <b>127.0.0.1:4444</b>, "
            "SOCKS <b>127.0.0.1:4447</b>.\nUse Tor for the clearnet; use I2P for "
            "I2P-native services.</small>")
        hint.set_xalign(0); hint.set_line_wrap(True)
        root.pack_start(hint, False, False, 0)

        self.refresh()
        GLib.timeout_add(REFRESH_MS, self.refresh)

    # --- actions ---
    def on_toggle(self, _btn):
        action = "stop" if service_active() else "start"
        rc, out = svc_action(action)
        if rc != 0:
            self.error_dialog(f"Could not {action} i2pd:\n{out}")
        self.refresh()

    def on_restart(self, _btn):
        rc, out = svc_action("restart")
        if rc != 0:
            self.error_dialog(f"Could not restart i2pd:\n{out}")
        self.refresh()

    def on_edit_tunnels(self, _btn):
        # The file is root-owned, so elevate a graphical editor with pkexec.
        # Try a few editors so this works across the DE options we ship.
        for editor in ("mousepad", "gedit", "kate", "nano"):
            rc, _ = run(["which", editor])
            if rc == 0:
                subprocess.Popen(["pkexec", editor, TUNNELS_CONF])
                return
        self.error_dialog(f"No graphical editor found.\nEdit {TUNNELS_CONF} manually.")

    def open_url(self, url):
        subprocess.Popen(["xdg-open", url])

    # --- refresh loop ---
    def refresh(self, *_):
        active = service_active()
        if active:
            self.status_lbl.set_markup("<b>I2P is running</b>")
            self.toggle_btn.set_label("Stop I2P")
        else:
            self.status_lbl.set_markup("<b>I2P is stopped</b>")
            self.toggle_btn.set_label("Start I2P")

        stats = fetch_console_stats() if active else None
        if stats:
            for key, widget in self.fields.items():
                widget.set_label(stats.get(key, "—") or "—")
        else:
            for widget in self.fields.values():
                widget.set_label("—" if not active else "starting…")
        return True  # keep the GLib timeout alive

    def error_dialog(self, msg):
        d = Gtk.MessageDialog(transient_for=self, modal=True,
                              message_type=Gtk.MessageType.ERROR,
                              buttons=Gtk.ButtonsType.CLOSE, text="I2P Manager")
        d.format_secondary_text(msg)
        d.run(); d.destroy()


def main():
    win = I2PManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
