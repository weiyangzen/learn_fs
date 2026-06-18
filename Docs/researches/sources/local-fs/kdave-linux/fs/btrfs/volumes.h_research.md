# File Research: sources/local-fs/kdave-linux/fs/btrfs/volumes.h

## Role

`volumes.h` is the central Btrfs volume/device/chunk mapping interface. It defines the in-memory objects and public APIs used to manage multi-device filesystems, RAID profiles, chunk maps, device statistics, discard mappings, block-to-stripe translation, device replacement, balance, grow/shrink, and swapfile pinning.

## Main Definitions

- `BTRFS_STRIPE_LEN`, `BTRFS_STRIPE_LEN_SHIFT`, and related helpers define the 64 KiB stripe unit used throughout Btrfs chunk mapping.
- `enum btrfs_raid_types` maps on-disk block group profile bits to compact raid indexes. Compile-time assertions lock in expected profile ordering.
- `struct btrfs_device` represents a filesystem device, including block device handles, device id, sizes, usage counters, zoned-device metadata, device state bits, stats, sysfs kobjects, flush state, scrub state, allocation state, and per-profile temporary accounting.
- `struct btrfs_fs_devices` represents a set of devices belonging to one filesystem UUID/metadata UUID. It tracks open/missing/rw/total devices, seed devices, allocation lists, mount state, sysfs state, read policy, and per-profile available-space estimates.
- `struct btrfs_io_context` carries logical-to-physical mapping results for submitted I/O, including stripes, mirror selection, replace-target duplication, RAID56 full-stripe layout, and raid-stripe-tree ordering metadata.
- `struct btrfs_chunk_map` describes a logical chunk: logical start/length, stripe size, RAID type, stripe count, and per-stripe physical mappings.
- `struct btrfs_raid_attr` declares RAID profile properties: minimum/maximum device counts, copies/parity, tolerated failures, profile name, and block group flag.
- `struct btrfs_balance_control` and `struct btrfs_dev_lookup_args` support balance operations and device lookup by devid, uuid, fsid, devt, or missing-device state.

## Important Behavior

Device size fields `total_bytes`, `disk_total_bytes`, and `bytes_used` use generated accessors. On 32-bit SMP builds, seqcount protection avoids torn 64-bit reads; on 32-bit preemptible builds, preemption is disabled around access; on wider or non-preempt configurations direct access is used.

Device statistics helpers update individual stat atomics and `dev_stats_ccnt` with memory barriers so transaction-time stat flushing can observe consistent changes.

Mapping APIs declared here are the core bridge from logical filesystem addresses to device stripes:

- `btrfs_map_block`
- `btrfs_map_repair_block`
- `btrfs_map_discard`
- `btrfs_find_chunk_map`
- `btrfs_get_chunk_map`
- `btrfs_remove_chunk_map`

Volume management declarations cover scanning/opening/closing devices, adding/removing devices, resizing devices, balance/resume/recover/pause/cancel, chunk creation/removal, superblock reading, degradability checks, and per-profile availability.

## Interactions

This header is consumed by much of Btrfs: chunk allocation, bio submission, scrub, dev replace, balance, zoned support, sysfs, and ioctl paths. `zoned.h` depends directly on `struct btrfs_device`, `struct btrfs_fs_devices`, and chunk/stripe layout definitions from this file.

## Notable Constraints

- `BTRFS_MAX_DATA_CHUNK_SIZE` limits data chunks to 10 GiB.
- `BTRFS_MAX_DISCARD_CHUNK_SIZE` limits one discard request to 1 GiB.
- `BTRFS_RAID1_MAX_MIRRORS` is currently 4 and must stay synchronized with RAID attributes.
- `BTRFS_MAX_DEVS` and `BTRFS_MAX_DEVS_SYS_CHUNK` derive maximum stripe counts from item sizes.
- Device name access is RCU-protected and returns `"<missing disk>"` for missing devices.
