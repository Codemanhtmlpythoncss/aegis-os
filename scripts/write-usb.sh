#!/bin/sh
# write-usb.sh — write an Aegis ISO to a USB stick (macOS or Linux). The ISO is a
# hybrid image, so the stick boots Aegis live/amnesic. THIS ERASES THE TARGET.
#
# Usage: ./scripts/write-usb.sh <aegis.iso> [device]
#   - with no device, it lists candidates and exits so you can pick one
#   - then re-run with the device, e.g.  ./scripts/write-usb.sh aegis-arm64-*.iso /dev/disk4
set -eu

ISO="${1:-}"
DEV="${2:-}"
[ -n "$ISO" ] && [ -f "$ISO" ] || { echo "usage: $0 <aegis.iso> [device]"; exit 1; }

OS="$(uname -s)"
list_devices() {
  if [ "$OS" = Darwin ]; then
    echo "External / removable disks:"; diskutil list external physical 2>/dev/null || diskutil list
    echo; echo "Re-run:  $0 \"$ISO\" /dev/diskN   (use the whole disk, e.g. /dev/disk4)"
  else
    echo "Removable disks:"; lsblk -dpo NAME,SIZE,TRAN,MODEL 2>/dev/null | grep -iE "usb|NAME" || lsblk -dpo NAME,SIZE,MODEL
    echo; echo "Re-run:  $0 \"$ISO\" /dev/sdX"
  fi
}

if [ -z "$DEV" ]; then list_devices; exit 0; fi

echo "About to ERASE $DEV and write $ISO to it."
if [ "$OS" = Darwin ]; then
  diskutil info "$DEV" 2>/dev/null | grep -iE "Device / Media Name|Disk Size|Protocol|Removable" || true
else
  lsblk -dpo NAME,SIZE,TRAN,MODEL "$DEV" 2>/dev/null || true
fi
printf 'Type the device path again to confirm: '
read -r CONFIRM
[ "$CONFIRM" = "$DEV" ] || { echo "Mismatch — aborted."; exit 1; }

if [ "$OS" = Darwin ]; then
  RDEV="$(echo "$DEV" | sed 's#/dev/disk#/dev/rdisk#')"   # raw device = much faster
  diskutil unmountDisk "$DEV"
  echo "Writing (sudo)…"; sudo dd if="$ISO" of="$RDEV" bs=4m
  sync; diskutil eject "$DEV" || true
else
  echo "Writing (sudo)…"; sudo dd if="$ISO" of="$DEV" bs=16M status=progress oflag=sync
  sync
fi
echo "Done. You can boot $DEV as Aegis (live/amnesic)."
