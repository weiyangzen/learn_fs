# File Research: sources/os/linux/linux/fs/btrfs/free-space-cache.h

## Purpose
Declares the in-memory free-space cache structures and public API implemented by `free-space-cache.c`.

## Main Types
- `enum btrfs_trim_state`
  - `BTRFS_TRIM_STATE_UNTRIMMED`
  - `BTRFS_TRIM_STATE_TRIMMED`
  - `BTRFS_TRIM_STATE_TRIMMING`
- `struct btrfs_free_space`
  - rb-tree nodes for offset and size indexes.
  - `offset`, `bytes`, `max_extent_size`.
  - optional `bitmap`.
  - temporary `list` linkage.
  - trim state and bitmap extent count.
- `struct btrfs_free_space_ctl`
  - spinlock-protected rb-tree indexes.
  - total free-space counters and bitmap/extent thresholds.
  - discardable extent/byte delta arrays.
  - owning block group.
  - cache writeout mutex and active trimming range list.
- `struct btrfs_free_space_op`
  - strategy callback deciding when to use bitmap representation.
- `struct btrfs_io_ctl`
  - page-array cursor and metadata for serializing/deserializing v1 cache inodes.

## Inline Helpers
- `btrfs_free_space_trimmed()` tests for fully trimmed entries.
- `btrfs_free_space_trimming_bitmap()` identifies bitmap entries currently being trimmed.
- `btrfs_trim_interrupted()` checks fatal signals or freezer state.

## Public API Groups
- Slab lifecycle: `btrfs_free_space_init()`, `btrfs_free_space_exit()`.
- Cache inode operations: lookup, create, remove, truncate, load, write, wait.
- In-memory free-space mutation/allocation: add, remove, dump, find allocation space.
- Cluster allocation: initialize, find cluster, allocate from cluster, return cluster.
- Discard trimming: trim entire block group, extents only, bitmaps only, fully remapped groups.
- Space cache v1 toggling: `btrfs_free_space_cache_v1_active()`, `btrfs_set_free_space_cache_v1_active()`.
- Sanity-test helpers when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.

## Design Notes
This header exposes both the allocator-facing API and the cache-inode API, so it is shared by block-group/extent allocation code, discard code, transaction/cache writeout paths, and tests.
