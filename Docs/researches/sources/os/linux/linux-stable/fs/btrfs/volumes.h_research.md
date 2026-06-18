# File Research: sources/os/linux/linux-stable/fs/btrfs/volumes.h

## Purpose

`volumes.h` is the shared declaration surface for Btrfs multi-device, chunk mapping, RAID profile, device statistics, device lookup, and block-to-device IO mapping code. It defines the core in-memory structures used by `volumes.c`, zoned support, device replace, scrub, balance, and lower-level bio submission.

## Main Concepts

- Defines Btrfs stripe constants: `BTRFS_STRIPE_LEN`, shift, and mask.
- Converts on-disk block group profile bits to internal `enum btrfs_raid_types` with compile-time static assertions.
- Defines `struct btrfs_device`, the per-device runtime state:
  - backing block device/file pointers
  - size accounting: total, disk total, used bytes, committed sizes
  - device identity: devid, uuid, devt, name
  - state bits for writable, missing, replace target, flush failures, discovered item
  - zoned info pointer
  - scrub, sysfs, statistics, allocation-state tracking
- Defines `struct btrfs_fs_devices`, the filesystem-level device set:
  - fsid and metadata_uuid handling
  - device counts, missing/open/rw devices
  - device lists and seed list
  - mount-hold lifecycle counters
  - mount/device capability flags
  - sysfs kobjects
  - chunk allocation and mirrored read policy
  - per-profile available-space cache
- Defines IO mapping structures:
  - `struct btrfs_io_stripe`
  - `struct btrfs_discard_stripe`
  - `struct btrfs_io_context`
  - `struct btrfs_chunk_map`
- Defines balancing and device lookup helper structures.
- Declares major exported routines for device scanning/opening/closing, chunk creation/removal, block mapping, balance, stats, device replace cleanup, chunk-map lookup, superblock reads, and per-profile availability.

## Important Details

- 64-bit device counters get generated getters/setters. On 32-bit SMP, seqcount protects torn reads. On 32-bit preemptible builds, preemption is disabled around direct access.
- `BTRFS_RAID_SINGLE` is special because it has no on-disk profile bit.
- `BTRFS_MAX_DEVS` and `BTRFS_MAX_DEVS_SYS_CHUNK` derive maximum stripe counts from item/system-chunk array capacity.
- `struct btrfs_io_context` carries both logical mapping and device-replace duplication state. RAID56 has special full-stripe metadata and replace-source tracking.
- `btrfs_free_chunk_map()` is refcounted and asserts the RB node is detached before freeing.
- Device stat helpers update `dev_stats_ccnt` with memory barriers so transaction-time stat persistence sees ordered values.
- `btrfs_get_per_profile_avail()` reads the cached profile estimate under `per_profile_lock` and treats `U64_MAX` as unavailable.
- `btrfs_op()` maps write and zone-append bios to `BTRFS_MAP_WRITE`, reads to `BTRFS_MAP_READ`, and warns on unexpected bio ops.

## Dependencies

This header depends on Linux block-device, bio, atomic, list, mutex, kobject, refcount, completion, rbtree, and UAPI Btrfs tree definitions. It also includes Btrfs-local `messages.h`, `extent-io-tree.h`, and `fs.h`.

## Research Notes

This file is architectural glue. Changes here affect many Btrfs subsystems because the structures encode shared invariants for device state, chunk mapping, RAID behavior, zoned support, and device statistics. The static assertions around RAID indexes and stripe size are especially important because they guard assumptions shared with on-disk formats and mapping code.
