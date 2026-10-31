# Aegis OS — Threat Model

A security tool only makes sense against a defined adversary. Here is what Aegis is and
isn't built for. Be honest with yourself about which row you're in.

## Protects reasonably well against

- **Local network / ISP snooping** — all traffic is forced through Tor/I2P; the fail-closed
  firewall prevents accidental clearnet leaks.
- **Website tracking & fingerprinting** — *if* you use Tor Browser or Mullvad Browser (shared
  fingerprint). Hardened Firefox helps with tracking but is more uniquely identifiable.
- **Forensic recovery after shutdown** — amnesic mode + RAM wipe leave little on disk/RAM.
- **Casual device fingerprinting on Wi-Fi** — MAC randomization changes your hardware identity.
- **Malicious USB in a brief unattended window** — USBGuard blocks unapproved devices.
- **Metadata leaks in shared files** — mat2 strips identifying metadata before you send.

## Does NOT protect against

- **Global passive adversary / end-to-end traffic correlation.** If someone can watch both
  your entry and your destination, timing analysis can deanonymize Tor *and* I2P. No low-
  latency network solves this.
- **Browser / application 0-days.** This is how real deanonymizations happen. Sandboxing
  (firejail/AppArmor) raises the bar; it is not a guarantee. Keep software updated.
- **Hardware implants, compromised firmware/BIOS, or a hypervisor below you.** Aegis runs
  *on* the hardware; it can't vouch for it. Verified/Secure Boot helps a little.
- **You logging into your real accounts.** Anonymity networks don't help if you sign into
  your named email. Operational security is on you.
- **Kernel-level exploits crossing the firejail/AppArmor boundary.** For hard isolation
  guarantees use Qubes OS (Xen) instead.
- **Coercion / rubber-hose.** Encryption doesn't help when you're compelled to unlock it.
  (LUKS "detached header" + plausible-deniability setups only go so far — don't over-trust them.)

## On "being invisible"

Aegis's stealth features make you **low-profile**, not invisible. Realistically:

- **What they do:** stop your machine announcing itself on the local network (no mDNS/Avahi,
  LLMNR, NetBIOS, no hostname in DHCP), remove a clearnet NTP beacon (time comes over Tor),
  turn off IPv6 and radios, randomize your MAC, and reduce the TCP/IP fingerprint. To a
  passive observer on the same Wi-Fi, Aegis is much quieter than a normal laptop.
- **What they can't do:** hide that *traffic exists*. Your ISP/Wi-Fi operator can still see
  that you are connected and that you are talking to the Tor network (unless you use a
  **bridge/pluggable transport** — enable obfs4 in `torrc`). They can't see *what* or *where*,
  but "this device is using Tor" is itself observable without bridges.
- **No low-latency system defeats a global passive adversary.** Someone who can watch both
  ends can still correlate traffic. Invisibility against that adversary is not on offer — by
  Aegis or by anything else in this class.

If "nobody can tell I'm online at all" is the requirement, no software OS delivers it; that's
a question of RF/physical opsec, not a distro.

## Operational notes

- The strongest config is **Tor Browser + amnesic mode + Tor transparent firewall**, which is
  essentially the Tails posture, plus the extra hardening Aegis adds.
- Turn **off** MAC randomization on networks that bind your identity to a MAC (some captive
  portals, corporate networks) — randomizing there can *draw attention* instead of hiding you.
- "Both Tor and I2P at once" is convenient but enlarges your footprint. Prefer picking the
  right network per task.
