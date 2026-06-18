# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mount.h

## Purpose
Defines the central `struct xfs_mount`, mount feature bits, operational state bits, shutdown flags, counter helpers, group geometry, error configuration, and public mount/counter APIs.

## Main Types
`struct xfs_mount` stores the in-core superblock, VFS superblock, log/AIL pointers, device targets, root and metadata inodes, quota state, directory geometry, workqueues, btree geometry, allocation/realtime group geometry, counters, mount features, opstate bits, health/debug/sysfs state, zoned state, inodegc state, and UUID table index.

`struct xfs_groups` describes allocation-group and realtime-group geometry, sparse group addressing, device start offset, and maximum atomic write unit. `struct xfs_freecounter` wraps per-cpu free counts plus reserve accounting. `struct xfs_error_cfg` stores retry configuration for error classes.

## Feature and State Helpers
The header defines active filesystem feature bits such as CRCs, reflink, rmapbt, realtime, metadir, zoned, and mount-option features such as discard, filestreams, DAX policy, norecovery, and nouuid. Inline helpers test or add features. Opstate helpers atomically test/set/clear clean, shutdown, inode32, readonly, inodegc/blockgc, quota resume, logged xattrs, and zonegc state.

## Public API
Declares mount/unmount, superblock read/free, writable checks, device readonly checks, freecounter operations, summary recalc forcing, log incompat feature management, delayed allocation accounting, atomic write option validation, and group-type-to-buftarg mapping.

## Compile-Time Behavior
Quota opstate helpers become no-ops when quota support is disabled. Some v4-era feature checks are compiled as always true when v4 support is disabled, allowing dead-code elimination.
