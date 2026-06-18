# File Research: sources/os/linux/linux/fs/btrfs/scrub.h

## Purpose
Declares the public Btrfs scrub control API used by the rest of the filesystem.

## Interfaces
- `btrfs_scrub_dev()`: starts a scrub or device-replace scrub for a specific device id and physical range, optionally returning `btrfs_scrub_progress`.
- `btrfs_scrub_pause()` and `btrfs_scrub_continue()`: coordinate transaction-safe pausing and resuming of active scrub workers.
- `btrfs_scrub_cancel()`: cancels all active scrubs for a filesystem.
- `btrfs_scrub_cancel_dev()`: cancels the scrub associated with one device.
- `btrfs_scrub_progress()`: copies the current progress for a device or reports that no scrub is active.

## Dependencies
Forward-declares `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress`, and includes `<linux/types.h>` for fixed-width integer and boolean types used in the prototypes.
