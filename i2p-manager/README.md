# I2P Manager

A small GTK3 front-end for the system `i2pd` router. It does **not** reimplement I2P —
it drives the `i2pd` systemd service and reads live stats from the i2pd web console
(`http://127.0.0.1:7070`), which keeps it tiny.

Features:
- Start / stop / restart I2P (via `pkexec systemctl`).
- Live status: network status, uptime, data in/out, known routers, client tunnels.
- Open the full router console in the browser.
- Edit `/etc/i2pd/tunnels.conf` (client/server tunnels, eepsites) in a graphical editor.

Run: `aegis-i2p-manager` (installed to `/usr/local/bin` by the build), or during
development: `python3 i2p_manager.py`.

Needs: `python3-gi`, `gir1.2-gtk-3.0`, a running `i2pd`. Browser proxies for `.i2p`:
HTTP `127.0.0.1:4444`, SOCKS `127.0.0.1:4447`.
