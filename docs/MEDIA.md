# Aegis on USB, DVD, and permanent media (SSD/HDD)

**One image does all of it.** `aegis-<arch>.iso` is a *hybrid* ISO — it boots from a
DVD **and** from a USB stick, and it carries the installer that puts Aegis permanently
onto an SSD. You don't need separate downloads.

## 1. USB stick — run Aegis live (amnesic)

Writing the ISO to a USB stick gives you a bootable, **amnesic** Aegis you can carry and
run on almost any machine. Nothing is written to the computer's disk.

Use the helper (it shows the target and asks before erasing):

```bash
./scripts/write-usb.sh aegis-arm64-YYYYMMDD.iso        # it lists devices, then you pick
```

or do it by hand:

- **macOS:** `diskutil list` → unmount the stick → `sudo dd if=aegis-*.iso of=/dev/rdiskN bs=4m`
- **Linux:** `lsblk` → `sudo dd if=aegis-*.iso of=/dev/sdX bs=16M status=progress oflag=sync`

> Double-check the device — `dd` erases it completely.

**Encrypted persistence** (optional, Tails-style): a LUKS-encrypted volume on the same
stick so *some* things survive reboots while the rest stays amnesic — this is on the roadmap
(`docs/SECURITY.md` #49); for now the USB session is fully amnesic.

## 2. Permanent install — SSD / HDD (encrypted)

For a daily-driver install on an internal or external **SSD**:

1. Boot the ISO (from USB or a VM).
2. Double-click **Install Aegis** on the desktop.
3. Choose your options (Tor/I2P, browser, desktop, MAC spoofing, compartmentalization…).
4. In the partitioning step, tick **Encrypt system** for full-disk LUKS.
5. Calamares installs Aegis permanently to the SSD, runs `aegis-apply`, and removes the
   installer. On next boot you get your encrypted, installed Aegis — no live media needed.

This is the "permanent media" path. The installed system is a normal bootable OS on the
SSD (with the Aegis hardening baked in), not an amnesic live session.

## 3. DVD

`sudo growisofs -dvd-compat -Z /dev/sr0=aegis-*.iso`, or any disc-burning app. (USB is
faster and reusable; DVD is there if you need read-only boot media.)

## Which do I want?

| Goal | Use |
|------|-----|
| Carry it, leave no trace on the PC | **USB**, live/amnesic |
| Install it for daily use on a laptop/SSD | Boot it, **Install Aegis** → SSD (encrypted) |
| Try it quickly | A **VM** (see `docs/BUILD.md` for QEMU) |
