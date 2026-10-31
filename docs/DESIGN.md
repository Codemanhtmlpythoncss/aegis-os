# Aegis OS — Design & Architecture

> **Codename "Aegis"** is a placeholder. Rename freely (see `profiles/*.conf` → `AEGIS_NAME`).

Aegis is a Debian-based, amnesic-by-default privacy OS that borrows the best idea from
each of three projects instead of cloning any one of them:

| Source    | Idea we take                                              | How Aegis implements it |
|-----------|-----------------------------------------------------------|-------------------------|
| **Tails** | Amnesic live system, forced-anonymity firewall, RAM wipe  | live-build image + fail-closed nftables + `ram_wipe` |
| **Whonix**| Transparent gateway routing so apps *can't* leak the real IP | nftables Tor transproxy (single-host variant of the Whonix gateway) |
| **Qubes** | Compartmentalization / least privilege                    | per-app sandboxing with **firejail + bubblewrap + AppArmor** (lightweight; not a Xen hypervisor — see "Honest limits") |

The goal you stated — *"secure but not resource-stealing like Tails"* — drives several
concrete choices: **XFCE** (not GNOME), **i2pd** (C++, not the Java I2P router), optional
**zram** instead of forced RAM-only operation, and no telemetry anywhere.

---

## Honest limits (read this first)

Security tooling is worthless if you believe things about it that aren't true, so:

1. **"Tor got cracked by the CIA" is not accurate.** Tor's protocol has not been broken.
   What *has* happened historically: (a) **traffic-correlation** attacks by adversaries who
   can watch both ends of a circuit, (b) **malicious relays**, and (c) **browser exploits** —
   e.g. the FBI's 2015 "Playpen" operation used a Firefox 0-day (an NIT), *not* a break of
   Tor itself. The takeaways that actually shape this design: the endpoint (your browser) is
   the soft target, and no single network is a silver bullet. That's why Aegis ships
   **defense in depth** and lets you run **Tor and I2P**, not one "trusted" network.

2. **I2P is not a strictly-better Tor.** I2P is excellent for in-network services (eepsites,
   torrents, messaging) with garlic routing and no central directory. But it has a **smaller
   anonymity set**, fewer outproxies, and far less academic scrutiny than Tor, and it is
   **weaker for anonymous access to the regular clearnet**. Rule of thumb Aegis encodes:
   **Tor for exiting to the clearnet, I2P for I2P-native services.**

3. **Hardened Firefox ≠ Tor Browser for anonymity.** You asked for Firefox + extensions
   (not Chromium — good, we honor that). But against *fingerprinting*, Tor Browser and
   **Mullvad Browser** (same engine, both non-Chromium) are much stronger because thousands
   of users share one fingerprint. Aegis therefore offers all three and labels the trade-off
   in the installer rather than pretending hardened Firefox is anonymous.

4. **"Qubes-grade isolation" has a hard ceiling here — be honest about it.** True Qubes
   security comes from a **Xen type-1 hypervisor** giving each qube its own kernel, with an
   isolated dom0 and VM-based `sys-net`/`sys-firewall`. A single live distro **cannot** be
   that; "Qubes-grade" bolted onto Debian would be a lie. What Aegis offers are the two best
   approximations you *can* do on one machine, as installer options:
   - **Sandbox (default):** firejail + bubblewrap + AppArmor sandbox every supported app by
     default (`firecfg`), plus `aegis-dispvm` for throwaway per-app sandboxes. Real
     *process-level* isolation — but a kernel bug can still cross it.
   - **VM isolation (KVM):** `aegis-vm-setup` builds an isolated libvirt network forced
     through Tor (the **Whonix** model), so a workstation VM gets *kernel-level* separation
     and can't learn your real IP. Strong — but it's KVM, not Xen, so still not literally
     Qubes. **If your threat model is nation-state, run actual Qubes OS.**

5. **"Install all of Kali" is a loud opt-in, not the default.** The full Kali toolset
   adds thousands of packages, services, and SUID binaries — i.e. **attack surface** — which
   is the opposite of a hardened daily driver. In Aegis it's an **installer checkbox**
   (default off) with a clear warning, and if you turn it on, the installer tells you the
   Tor fail-closed firewall will block pentest traffic until you switch to **direct** mode.
   Offensive tooling and locked-down anonymity genuinely conflict; Aegis makes you choose
   on purpose rather than by accident.

---

## One ISO, all choices in the installer

There is a **single universal ISO per architecture**. It boots to a hardened XFCE live
session (already routing through Tor), and everything else is chosen in the installer:

1. **Aegis Options** (`setup-wizard/aegis_options.py`) — a GTK dialog for the network mode,
   browser, desktop, MAC spoofing, Kali tier, and hardening toggles. It writes the choices
   to `/etc/calamares/aegis-options.env`.
2. **Calamares** — the standard distro installer handles locale/keyboard, **disk
   partitioning with full-disk LUKS encryption**, users, and bootloader.
3. **`aegis-apply`** — runs inside the freshly-installed target, reads the options file,
   installs the chosen browser/desktop/Kali tier, flips the toggles, and removes the
   installer from the installed system.

No custom Calamares C++/PythonQt module is needed (the options are gathered before
Calamares starts), which keeps the installer easy to build and maintain.

---

## Architecture layers

```
┌──────────────────────────────────────────────────────────────┐
│ Applications (sandboxed: firejail + AppArmor profiles)         │
│   Firefox-hardened / Tor Browser / Mullvad · KeePassXC · mat2  │
├──────────────────────────────────────────────────────────────┤
│ Aegis control apps                                             │
│   • Setup Wizard  (first-boot + Calamares module)              │
│   • I2P Manager   (GTK front-end over the i2pd console/API)    │
├──────────────────────────────────────────────────────────────┤
│ Anonymity routing                                              │
│   Tor daemon ── nftables transparent proxy (fail-closed)       │
│   i2pd  ────── SOCKS/HTTP + eepsite tunnels                    │
├──────────────────────────────────────────────────────────────┤
│ Hardening                                                      │
│   sysctl · kernel lockdown · AppArmor · USBGuard · MAC random  │
│   randomized hostname/machine-id · UTC · RAM wipe on shutdown  │
├──────────────────────────────────────────────────────────────┤
│ Base: Debian (trixie) · XFCE (swappable DE) · amd64 + arm64    │
└──────────────────────────────────────────────────────────────┘
```

## Installer options (what the user picks)

The Aegis Options dialog (`setup-wizard/aegis_options.py`) exposes exactly the toggles
you asked for:

- **Network mode:** Tor transparent / I2P / both / direct (clearnet)
- **Browser:** Tor Browser · Mullvad Browser · hardened Firefox ESR · LibreWolf (never Chromium)
- **Desktop:** XFCE (default) · KDE Plasma · GNOME · i3
- **MAC spoofing:** on by default (random per-connection) / off
- **Offensive toolkit:** none (default) / Kali headless / default / large
- **Compartmentalization:** sandbox (firejail, default) / VM isolation (KVM, Whonix-style) / none
- **Stealth networking:** quiet on the LAN — no mDNS/Avahi/LLMNR/NetBIOS, no DHCP hostname,
  time over Tor (no clearnet NTP), IPv6 off, radios off
- **Hardening:** full-disk LUKS encryption · amnesic-by-default · USBGuard · RAM-wipe

Encryption itself is done by Calamares' partitioning step (tick "Encrypt system").
The same dialog, launched as **Aegis Control** after install, re-shows the two options
that can change on a running system (network mode, MAC spoofing) and applies them live.

Architecture (`amd64` vs `arm64`) is the one build-time choice — see `docs/BUILD.md`.

## Beyond the brief — extra hardening Aegis bakes in

- **Fail-closed firewall** (default-deny nftables) — nothing reaches the network except via
  the selected anonymity layer.
- **RAM wipe on shutdown** (`sdmem`-style) so keys don't survive a cold-boot grab.
- **USBGuard** — new USB devices are blocked until you approve them (anti-BadUSB / "evil maid").
- **Metadata scrubbing** — `mat2` + right-click Thunar action to strip EXIF/doc metadata.
- **Randomized identity each boot** — hostname, `machine-id`, timezone pinned to UTC.
- **Kernel hardening** — `lockdown=confidentiality`, `slab_nomerge`, `init_on_free`, `mce=0`,
  disabled uncommon network protocols and `kmod` autoloading, optional **hardened_malloc**.
- **Encrypted persistence** (LUKS) à la Tails, opt-in only.
- **Reproducible-build goal** + signed ISO/checksums (see `docs/BUILD.md`).
- **No telemetry** — popcon, whoopsie, GeoClue, and connectivity-check phone-homes removed.

See `THREAT-MODEL.md` for who this does and does not protect against.
