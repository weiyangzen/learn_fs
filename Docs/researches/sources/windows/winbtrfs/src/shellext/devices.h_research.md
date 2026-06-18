# File Research: sources/windows/winbtrfs/src/shellext/devices.h

Read status: complete, 156 lines.

This header defines data structures and classes for the Btrfs device add/resize dialogs.

Key declarations:
- `device` stores PnP path, friendly name, drive letter, detected filesystem type, disk and partition numbers, size, Btrfs filesystem/device UUIDs, and flags for ignore, multi-device, disk, and partition presence.
- `fs_identifier` describes filesystem magic probes by display name, magic bytes, magic length, byte offset inside a 4 KiB buffer, and KiB read offset.
- `fs_ident` is a static table of filesystem signatures compiled from libblkid information. It includes Btrfs magic `_BHRfS_M` at superblock offset 64 KiB plus many common filesystems.
- `BtrfsDeviceAdd` declares dialog, display, and add-device methods plus selected-device state.
- `BtrfsDeviceResize` declares dialog, display, and resize methods plus current device information and pending size.

Integration:
- Implemented in `devices.cpp`.
- Used by exported callbacks `AddDeviceW`, `RemoveDeviceW`, and `ResizeDeviceW`.
- Depends on `../btrfsioctl.h` for `BTRFS_UUID` and `btrfs_device`.

Risk and maintenance notes:
- The header defines `fs_ident` as `const static`, so each translation unit including it gets its own copy. Currently it appears only intended for `devices.cpp`.
- Filesystem detection is magic-based and suitable for warning/display, not a complete validator.
