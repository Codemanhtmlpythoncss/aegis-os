# Aegis OS — Security Improvements (50+)

A living hardening catalog. Honest status tags so you always know what's real:

- 🟢 **added now** — implemented in this round of work
- ✅ **shipped** — already in Aegis before this round
- ⚙️ **installer** — a choice/toggle in the installer
- 🔭 **roadmap** — designed but not yet implemented (don't assume it's active)

> Hostname randomization (#3) is the specific item you asked for; the other 49 are
> the "50 more" — a mix of just-added, already-present, and planned. Nothing here is
> claimed as active unless its tag says so.

---

## Boot & hardware integrity
1. 🟢 **IOMMU / DMA-attack protection** — `intel_iommu=on amd_iommu=on efi=disable_early_pci_dma` block malicious PCIe/Thunderbolt devices from reading RAM.
2. 🟢 **Memory poisoning** — `init_on_alloc=1 init_on_free=1 page_poison=1` zero memory on alloc/free so freed secrets don't linger.
3. 🔭 **Thunderbolt/FireWire DMA lockout** — authorize-by-default off (`boltd`), blacklist FireWire SBP2.
4. 🔭 **UEFI Secure Boot** — signed shim + kernel so unsigned/tampered kernels won't boot.
5. 🔭 **dm-verity on the base squashfs** — cryptographic integrity of the read-only system image (Tails/Qubes style).
6. 🔭 **TPM2-sealed LUKS key / measured boot** — disk unlocks only if firmware+bootloader are unmodified (evil-maid defense).

## Kernel self-protection
7. ✅ **Kernel lockdown=confidentiality** — blocks ways userspace could read/modify the running kernel.
8. ✅ **SMT + CPU-vuln mitigations** — `mitigations=auto,nosmt` closes Spectre/MDS-class side channels.
9. ✅ **kexec disabled, ptrace_scope=2, kptr/dmesg restricted** — no live kernel replacement, no cross-process memory peeking, no kernel-pointer leaks.
10. ✅ **Unprivileged BPF off + JIT hardening** — shrinks a classic local-privesc surface.
11. ✅ **Unprivileged user namespaces restricted** — cuts a major exploit vector *(trade-off: some rootless sandboxes rely on userns; Aegis's firejail/bwrap are setuid so still work).*
12. ✅ **Maximum ASLR** — `randomize_va_space=2`, `randomize_kstack_offset=on`.
13. 🔭 **Module signature enforcement / lock module loading after boot** — prevents loading rootkit LKMs at runtime.

## Memory & processes
14. 🟢 **systemd daemon sandboxing** — tor & i2pd get `ProtectKernelTunables/Modules/Logs`, `RestrictNamespaces/SUIDSGID/Realtime`, `LockPersonality`, `ProtectClock`, `PrivateTmp`.
15. 🟢 **Core dumps disabled** — `Storage=none`, `suid_dumpable=0` so crashes don't write keys/plaintext to disk.
16. 🟢 **Default umask 077** — new files are private by default.
17. 🔭 **hardened_malloc** — GrapheneOS's hardened allocator preloaded system-wide (the `ld.so.preload` hook is already in place; needs the package built for Debian).
18. 🔭 **Per-daemon seccomp allowlists** — restrict tor/i2pd to the syscalls they actually use.

## Network & anonymity
19. ✅ **Fail-closed transparent Tor firewall** — nothing leaves the box except via Tor; leaks are dropped, not sent.
20. ✅ **DNS only through Tor** — plaintext DNS is blocked; no DNS leaks.
21. ✅ **Tor stream isolation** — separate circuits per destination/port to resist correlation.
22. ✅ **Time sync over Tor** — clearnet NTP disabled (no "this host exists" beacon).
23. ✅ **mDNS/Avahi/LLMNR/NetBIOS silenced** — the machine stops announcing itself on the LAN.
24. ✅ **IPv6 disabled** — prevents the classic v6-around-the-Tor-v4-transproxy leak.
25. ✅ **No hostname in DHCP** — `dhcp-send-hostname=false`.
26. ⚙️ **obfs4 bridges** — one toggle for censored networks *(torrc stub shipped; GUI toggle is roadmap)*.
27. 🔭 **VPN layering** — guided Tor-over-VPN / VPN-over-Tor with WireGuard.
28. ✅ **No listening services by default** — default-deny inbound firewall; nothing exposed.

## Identity & fingerprinting
29. 🟢 **Random hostname each boot** — `aegis-hostname`; the machine name is never a persistent ID *(optional fixed-generic mode à la Tails via `/etc/aegis/hostname.conf`)*.
30. 🟢 **Browser JIT off + ServiceWorkers/WebAudio/clipboard/device-enumeration off** — large cut to the browser's remote attack & fingerprint surface.
31. 🟢 **Always-on private browsing, no disk cache** — nothing browser-related persists.
32. ✅ **MAC randomization per connection** — hardware identity changes each time.
33. ✅ **Blanked machine-id (regenerated per boot)** — no stable install identifier.
34. ✅ **UTC clock** — no timezone leak.
35. ✅ **Browser anti-fingerprinting** — resistFingerprinting, no WebGL/WebRTC, Tor Browser/Mullvad options.
36. ✅ **mat2 metadata scrubbing** — strip EXIF/doc metadata before sharing files.
37. ✅ **No telemetry anywhere** — popcon, whoopsie, GeoClue, connectivity-check all removed.

## Sandboxing & isolation
38. ✅ **firejail sandbox-by-default** — `firecfg` sandboxes every supported app.
39. ✅ **Disposable per-app sandbox** — `aegis-dispvm` (throwaway home, wiped on exit).
40. ⚙️ **KVM VM isolation, Tor-only network** — `aegis-vm-setup`, the Whonix model (kernel-level separation; not Xen/Qubes).
41. ✅ **AppArmor enabled** — mandatory access control on supported profiles.
42. 🔭 **Custom AppArmor profiles** — tighter enforce-mode profiles for the browser, tor, i2pd.
43. 🔭 **Wayland session option** — smaller surface than X11 (no global keylogging); pending XFCE Wayland maturity.

## Anti-forensics & physical
44. ✅ **RAM wipe on shutdown** — overwrites memory to resist cold-boot key recovery.
45. ✅ **USBGuard** — new USB devices blocked until approved (anti-BadUSB / evil-maid).
46. 🟢 **Screen locker + Ctrl+Alt+Del disabled** — xfce4-screensaver lock; no accidental/forced reboot combo.
47. ✅ **Secure-delete / BleachBit** — wipe files and free space.
48. 🔭 **Panic wipe** — hotkey / USB-removal trigger that instantly wipes keys and powers off.

## Supply chain & maintenance
49. ⚙️/🔭 **Full-disk LUKS (default)** — ⚙️ via installer; 🔭 enforce Argon2id KDF + ensure encrypted (or no) swap.
50. 🔭 **Trustworthy distribution & updates** — reproducible builds (pinned Debian snapshot), **GPG-signed ISOs** (sha256 already published), **apt-over-Tor** updates, plus `auditd`/`AIDE` integrity monitoring and `unattended-upgrades` for security patches.

---

### Known trade-offs (honesty)
- **Restricting user namespaces (#11)** can break rootless Podman/Flatpak; Aegis's sandboxes use setuid helpers so they still work.
- **nosmt (#8)** can cost performance on some CPUs — the price of closing SMT side channels.
- **`noexec` on /tmp, /proc hidepid** (not yet enabled) can break some apps/session tooling; that's why they're roadmap, pending compatibility testing, not flipped on blindly.
- None of this defeats a **global passive adversary** or a **kernel/firmware/hardware compromise**. See [THREAT-MODEL.md](THREAT-MODEL.md).
