# File Research: sources/local-fs/btrfs-linux/fs/btrfs/scrub.h

## Purpose
Declares the Btrfs scrub public interface used by the rest of the filesystem. This header exposes only the scrub operations and keeps implementation details private to `scrub.c`.

## Contents
- Header guard: `BTRFS_SCRUB_H`.
- Includes `<linux/types.h>` for fixed-width integer and `bool`-related kernel types.
- Forward declarations:
  - `struct btrfs_fs_info`
  - `struct btrfs_device`
  - `struct btrfs_scrub_progress`

## Exported Functions
- `btrfs_scrub_dev(fs_info, devid, start, end, progress, readonly, is_dev_replace)`: starts scrub for a device physical range, optionally in readonly or dev-replace mode.
- `btrfs_scrub_pause(fs_info)`: blocks until active scrub workers reach pause points.
- `btrfs_scrub_continue(fs_info)`: releases a previous pause request.
- `btrfs_scrub_cancel(info)`: requests cancellation of active filesystem scrub runs.
- `btrfs_scrub_cancel_dev(dev)`: requests cancellation of the scrub tied to one device.
- `btrfs_scrub_progress(fs_info, devid, progress)`: reports current scrub progress for a device.

## Role In The Module Boundary
The header forms the control-plane API for scrub. Callers can start, pause, resume, cancel, and query scrub without depending on `scrub_ctx`, `scrub_stripe`, bitmap layout, worker logic, RAID handling, or repair internals.
