# Aegis OS packages

This is where Aegis stops being "a Debian remaster with hooks" and becomes a real
distribution: every Aegis component is a proper Debian package here, built by CI,
and (next) published to a signed APT repository. The live/installer ISO then just
installs `aegis-meta` from that repo instead of running a pile of build hooks — and
an installed system gets Aegis **and** Debian security updates via `apt upgrade`.

## Layout

Each subdirectory is a native Debian source package:

| Package          | What it provides                                                        |
|------------------|-------------------------------------------------------------------------|
| `aegis-base`     | kernel hardening (sysctl), module blacklists, AppArmor, OS branding     |
| `aegis-firewall` | `aegis-firewall` + `aegis-netmode.service` (fail-closed Tor firewall)   |
| `aegis-meta`     | metapackage that depends on all of the above (install this = Aegis OS)  |

More packages land here as the migration continues: `aegis-anon` (Tor/i2pd +
tordate), `aegis-live` (amnesic live session: autologin, random hostname,
wipe-on-removal), `aegis-desktop` (XFCE defaults/theme, no idle lock),
`aegis-control` (the Control Center GUI), `aegis-installer` (Calamares + apply).

## Building

Packages build in a Debian trixie environment (not on macOS). CI does this on
every push via `.github/workflows/packages.yml`. To build one by hand on Debian:

```bash
cd packages/aegis-base
dpkg-buildpackage -us -uc -b
# the .deb appears in packages/
```

## Versioning

Native packages (`3.0 (native)`), version tracks the Aegis release (currently
`1.2.0`). Bump the version by adding a new top block to each package's
`debian/changelog`.
