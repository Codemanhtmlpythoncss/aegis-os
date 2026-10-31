# Building Aegis OS

There is **one universal ISO per architecture**. You do **not** choose Tor/I2P,
browser, desktop, MAC spoofing, Kali, or encryption at build time — those are all
picked in the **on-ISO installer**. The only build-time choice is `amd64` vs `arm64`.

Aegis is built with Debian **live-build** (the tool Tails and Kali use). You need a
**Debian/Ubuntu host** (or a Debian VM/container). You **cannot build on macOS or
Windows directly** — run the build inside a Debian VM there.

## 1. Host prerequisites

```bash
sudo apt update
sudo apt install -y live-build git ca-certificates debootstrap xorriso \
    squashfs-tools mtools dosfstools
# Cross-arch only (building arm64 on amd64, or vice versa):
sudo apt install -y qemu-user-static binfmt-support
```

~15 GB free disk and a decent connection. The build runs as root.

## 2. Build

```bash
sudo ./build.sh --arch amd64      # normal PCs (BIOS + UEFI)
sudo ./build.sh --arch arm64      # UEFI arm64 (see note below)
```

Result: `aegis-<arch>-<date>.iso` and `aegis-<arch>-<date>.iso.sha256`.

`build.sh` is a thin wrapper: it stages the Aegis payload (control apps, Calamares
config, default live desktop) into the live-build `config/` tree, sets the
architecture, archive areas, bootloaders and the **hardened kernel command line**
(`init_on_free=1`, `lockdown=confidentiality`, `slab_nomerge`, `mitigations`…),
then runs `lb build`.

## 3. What the ISO does when you boot it

1. Boots to a hardened **XFCE live session** already routing through Tor (fail-closed),
   with MAC randomization on — so the live session itself is usable and private.
2. Double-click **Install Aegis** on the desktop. You get:
   - the **Aegis Options** dialog — network mode (Tor/I2P/both/direct), browser
     (Tor Browser / Mullvad / hardened Firefox / LibreWolf), desktop (XFCE/KDE/GNOME/i3),
     MAC spoofing, offensive (Kali) toolkit, and hardening toggles;
   - then **Calamares**, which does locale/keyboard, **disk partitioning with
     full-disk LUKS encryption**, user creation and bootloader install.
3. Calamares clones the hardened base to disk, then runs `aegis-apply` inside the
   new system to install your chosen browser/desktop/Kali tier and flip the toggles,
   and finally removes the installer from the installed system.

So "the installer manages the stuff" — there are no manual post-install steps.

## 4. ARM64 notes

- **amd64** boots on normal PCs and x86 VMs out of the box.
- **arm64** targets **UEFI arm64** (GRUB-EFI): QEMU `virt`, arm64 cloud, Apple-Silicon
  VMs (UTM/Parallels), UEFI-capable ARM boards.
- **Bare-metal SBCs** (Raspberry Pi, Pine64…) use **U-Boot + board DTBs**, not generic
  UEFI, and need a per-board image — not produced here yet. Start from Debian's arm64
  live images + the board's U-Boot.

## 5. Test in a VM first

```bash
# amd64
qemu-system-x86_64 -enable-kvm -m 4096 -smp 2 -cdrom aegis-amd64-*.iso -boot d
# arm64
qemu-system-aarch64 -M virt -cpu cortex-a72 -m 4096 \
  -bios /usr/share/AAVMF/AAVMF_CODE.fd -cdrom aegis-arm64-*.iso
```

## 6. Write to USB

```bash
sudo dd if=aegis-amd64-*.iso of=/dev/sdX bs=16M status=progress oflag=sync
# Double-check /dev/sdX — this erases the device.
```

## 7. Verify / sign

```bash
sha256sum -c aegis-amd64-*.iso.sha256
# For releases, sign and publish the key out-of-band:
gpg --armor --detach-sign aegis-amd64-*.iso
```

**Reproducible builds** are a goal: pin `--mirror` to `snapshot.debian.org` at a fixed
timestamp and keep `SOURCE_DATE_EPOCH` fixed so the same commit yields identical ISOs.

## 8. Customizing

- **Default live desktop / baseline:** `profiles/defaults.conf`.
- **What the installer can install:** `catalog/*.list.chroot` (package groups) and the
  logic in `config/includes.chroot/usr/local/bin/aegis-apply`.
- **Installer flow/branding:** `installer/calamares/`.
- **Hardening:** `config/includes.chroot/etc/sysctl.d/…`, `nftables-tor.conf`, hooks in
  `config/hooks/normal/`, and the kernel cmdline in `build.sh`.
