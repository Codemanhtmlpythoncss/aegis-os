# Aegis Options / Aegis Control

One GTK3 app, two roles:

- **`aegis_options.py --install`** — the installer's options screen. Shows all
  install-time choices (network mode, browser, desktop, MAC spoofing, Kali tier, and
  hardening toggles) and writes them to `/etc/calamares/aegis-options.env`. The
  `aegis-installer` wrapper runs this, then launches Calamares; `aegis-apply` acts on
  the file inside the target.

- **`aegis_options.py`** (no flag) — **Aegis Control**, launched after install. Only the
  options that can change on a running system (network mode, MAC spoofing) are editable
  and apply immediately via `aegis-firewall` / `aegis-mac-spoof`; install-only choices are
  shown disabled for reference.

Needs: `python3-gi`, `gir1.2-gtk-3.0`, and `pkexec` (PolicyKit) for privileged actions.
