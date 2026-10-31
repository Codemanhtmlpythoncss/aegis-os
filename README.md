<p align="center">
  <img src="assets/logo.svg" width="128" height="128" alt="Aegis OS logo">
</p>

# Aegis OS

A Debian-based, privacy-focused live OS that borrows from **Tails** (amnesic, forced-
anonymity firewall), **Whonix** (transparent Tor gateway routing) and **Qubes**
(compartmentalization) — tuned to be **light** (XFCE + i2pd, not Java I2P), with an
**I2P manager built in**, and a **graphical installer** where you choose everything:
Tor/I2P, a non-Chromium browser, desktop, MAC spoofing, optional Kali tools, and
full-disk encryption.

> **Status: buildable project scaffold, not a released ISO.** Every config, script and
> app here is real, but the ISO must be built on a Debian host (`./build.sh`) and then
> tested in a VM. It has not been built/booted in this environment (that needs Linux).
> **"Aegis" is a placeholder name** — rename in `profiles/defaults.conf` and the branding.

## Read the honesty first

- [`docs/DESIGN.md`](docs/DESIGN.md) — architecture + **honest limits** (incl. why "Tor was
  cracked by the CIA" isn't accurate, and why hardened Firefox ≠ Tor Browser for anonymity).
- [`docs/THREAT-MODEL.md`](docs/THREAT-MODEL.md) — what this does and does **not** protect you from.
- [`docs/SECURITY.md`](docs/SECURITY.md) — the 50-item hardening catalog with honest status tags (implemented / installer / roadmap).

## Quick start

On a Debian/Ubuntu host:

```bash
sudo apt install -y live-build debootstrap xorriso squashfs-tools mtools dosfstools
sudo ./build.sh --arch both        # or: --arch amd64 / --arch arm64
```

Boot the resulting `aegis-*.iso` in a VM, double-click **Install Aegis**, pick your
options, and let it install. Full details: [`docs/BUILD.md`](docs/BUILD.md).

**Prebuilt ISOs:** the GitHub Actions workflow (`.github/workflows/build.yml`) builds
**both** architectures on Linux runners and attaches them to a Release — so you can grab an
ISO without building, and anyone can still build their own. (ISOs can't be compiled on
macOS/Windows; CI or a Debian host does it.)

## How the pieces fit

```
build.sh ──> one universal live ISO per arch (amd64 / arm64)
                │  hardened XFCE live session, Tor fail-closed, i2pd, firefox-esr
                ▼
        "Install Aegis" (aegis-installer)
                │  1. aegis_options.py  -> /etc/calamares/aegis-options.env
                │  2. Calamares         -> partition + LUKS + users + bootloader
                │  3. aegis-apply       -> installs chosen browser/DE/Kali, flips toggles
                ▼
        installed, encrypted Aegis system
```

## Repository layout

| Path | What it is |
|------|------------|
| `build.sh` | Builds one ISO per architecture (the only build-time choice). |
| `profiles/defaults.conf` | Baseline for the live image. |
| `config/package-lists/` | Packages always in the live ISO (base, anonymity, privacy, installer). |
| `catalog/` | Optional package groups the **installer** adds to the target (DEs, browsers, Kali). |
| `config/hooks/normal/` | Build-time chroot hooks (hardening, Firefox prefs, apps, live installer). |
| `config/includes.chroot/` | Files baked into the image: firewall, sysctl, Tor/i2pd config, MAC & RAM-wipe scripts, systemd units, Firefox policy, control-app launchers. |
| `setup-wizard/aegis_options.py` | The installer's options dialog (and runtime **Aegis Control**). |
| `i2p-manager/i2p_manager.py` | The built-in **I2P Manager** GUI (drives i2pd). |
| `installer/calamares/` | Calamares `settings.conf`, branding, and the two shellprocess steps. |
| `config/includes.chroot/usr/local/bin/aegis-apply` | Post-install configurator (runs in the target). |
| `docs/` | Design, threat model, build guide. |

## Security features at a glance

Forced-anonymity **fail-closed Tor firewall** · **i2pd** with a GUI manager · hardened
**Firefox/Tor Browser/Mullvad/LibreWolf** (never Chromium) · **MAC randomization** ·
**full-disk LUKS** · **amnesic** live mode + **RAM wipe** on shutdown · **USBGuard** ·
**compartmentalization** — firejail sandbox-by-default + disposable sandboxes, or KVM
**VM isolation** with a Tor-only network (Whonix-style; not Xen/Qubes) · **stealth
networking** — no mDNS/LLMNR/NetBIOS, no DHCP hostname, time over Tor, IPv6 off, radios off ·
kernel hardening (`lockdown`, `init_on_free`, hardened_malloc) · **mat2** metadata scrubbing ·
randomized hostname/machine-id, UTC, **no telemetry** · optional **Kali** toolkit for
authorized testing.

See [`docs/DESIGN.md`](docs/DESIGN.md) for the reasoning behind each.
