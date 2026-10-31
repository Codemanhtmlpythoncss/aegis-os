# Aegis installer

The installer is **Calamares** (standard, battle-tested partitioning + LUKS encryption +
bootloader) plus a pre-step that gathers the Aegis-specific choices. No custom
C++/PythonQt Calamares module is required.

Flow (see also `../docs/BUILD.md`):

1. **`aegis-installer`** (on the live desktop) runs `aegis_options.py --install`, which
   writes `/etc/calamares/aegis-options.env`, then launches `pkexec calamares`.
2. **Calamares** (`calamares/settings.conf`) runs the normal install sequence. Two extra
   steps near the end:
   - `shellprocess-stage.conf` copies `aegis-options.env` into the target
     (`/etc/aegis/install-options.env`).
   - `shellprocess-apply.conf` runs `aegis-apply` inside the target chroot.
3. **`aegis-apply`** (`../config/includes.chroot/usr/local/bin/aegis-apply`) installs the
   chosen browser/desktop/Kali tier, flips the toggles, and purges the installer from the
   installed system.

## Files

- `calamares/settings.conf` — module sequence + branding reference.
- `calamares/branding/aegis/` — `branding.desc`, `show.qml` slideshow, placeholder logos
  (`logo.png`, `welcome.png` are 1×1 placeholders — replace with real art).
- `calamares/modules/shellprocess-stage.conf`, `shellprocess-apply.conf` — the two glue steps.

`build.sh` copies `calamares/` into the live image at `/etc/calamares/`. The live-installer
hook seeds the stock Calamares module examples (partition/users/bootloader/…) first, then
these overlay them.
