# File Research: sources/os/linux/linux-stable/fs/btrfs/scrub.h

## Purpose

This header declares the public Btrfs scrub control API used by the rest of the filesystem. It intentionally exposes only high-level scrub operations and forward-declares the involved Btrfs types.

## Exposed Types

The header forward-declares:
- `struct btrfs_fs_info`
- `struct btrfs_device`
- `struct btrfs_scrub_progress`

It includes `<linux/types.h>` for fixed-width integer and boolean type availability.

## Exported Functions

- `btrfs_scrub_dev(...)`: starts scrub or device-replace scrub for a device ID over a physical range, optionally returns progress, and supports readonly mode.
- `btrfs_scrub_pause(...)`: requests all running scrubs on the filesystem to pause.
- `btrfs_scrub_continue(...)`: releases a previous pause request.
- `btrfs_scrub_cancel(...)`: cancels currently running scrub work for the filesystem.
- `btrfs_scrub_cancel_dev(...)`: cancels scrub for one device.
- `btrfs_scrub_progress(...)`: reads the current progress counters for a device scrub.

## Design Role

`scrub.h` is a narrow subsystem boundary. All scrub internals, including stripe structures, bitmap state, repair workers, RAID56 parity logic, block-group coordination, and superblock validation, remain private to `scrub.c`. The rest of Btrfs interacts with scrub through these lifecycle/progress functions only.
