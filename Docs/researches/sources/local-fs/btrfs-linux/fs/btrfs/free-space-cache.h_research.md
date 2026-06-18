# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.h

## Summary
Declares the in-memory free-space cache data structures, trim-state model, cache inode I/O context, free-space allocator interfaces, cluster interfaces, trim interfaces, and cache-v1 feature controls.

## Main Contents
- `enum btrfs_trim_state` for untrimmed, trimmed, and in-progress bitmap trimming state.
- `struct btrfs_free_space` representing either an extent entry or bitmap entry.
- `struct btrfs_free_space_ctl` containing free-space rb-trees, counters, discard deltas, block-group ownership, writeout mutex, and trimming range list.
- `struct btrfs_free_space_op` hook for bitmap selection policy.
- `struct btrfs_io_ctl` page-buffer context for reading and writing cache inode contents.
- Function declarations for cache inode lifecycle, cache load/write, free-space mutation, allocation, clustering, trimming, and tests.

## Key Interfaces
The header exposes the allocator-facing APIs `btrfs_add_free_space()`, `btrfs_remove_free_space()`, `btrfs_find_space_for_alloc()`, and cluster allocation helpers, plus the persistence-facing APIs `load_free_space_cache()`, `btrfs_write_out_cache()`, and `btrfs_wait_cache_io()`.

## Important Details
`btrfs_free_space_trimmed()` and `btrfs_free_space_trimming_bitmap()` encode trim-state checks used by discard and allocator accounting. `btrfs_trim_interrupted()` treats fatal signals and freezer state as trim cancellation conditions.

Discard statistics use current/previous delta slots (`BTRFS_STAT_CURR`, `BTRFS_STAT_PREV`) so the discard subsystem can aggregate changes from each block group's free-space control.

`btrfs_io_ctl` is a low-level cursor over cache inode pages. It carries the current page pointer, page array, inode, filesystem info, page count, and serialized entry/bitmap counts.

## Risks
`struct btrfs_free_space` is used in both normal block-group trees and cluster trees; callers must respect which rb-node is currently linked and which lock protects it.

The trim state is per extent or per whole bitmap, not per bit. Bitmap trim state is therefore intentionally lossy, and callers must not interpret `TRIMMED` as proof that every historical fragment has perfect per-sector state.
