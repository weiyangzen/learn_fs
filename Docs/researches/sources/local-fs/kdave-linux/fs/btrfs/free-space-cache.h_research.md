# File Research: sources/local-fs/kdave-linux/fs/btrfs/free-space-cache.h

This header defines the in-memory free-space cache types and public API used by Btrfs block group caching, allocation, clustering, trimming, discard, and old space-cache v1 persistence.

Primary types:
- `enum btrfs_trim_state` tracks whether a free extent/bitmap is untrimmed, trimmed, or actively being trimmed.
- `struct btrfs_free_space` represents one free-space cache record, either an extent or bitmap, indexed by offset and by usable size.
- `struct btrfs_free_space_ctl` owns the rb-trees, counters, bitmap thresholds, block group pointer, operation table, trimming range list, and writeout mutex for one block group.
- `struct btrfs_free_space_op` lets a control decide whether a free-space record should be represented as a bitmap.
- `struct btrfs_io_ctl` is the page/cursor state used to serialize or read the v1 free-space cache inode format.

Important fields:
- `btrfs_free_space::offset`, `bytes`, `max_extent_size`, `bitmap`, `trim_state`, and `bitmap_extents` are the core allocator/discard state.
- `btrfs_free_space_ctl::free_space_offset` supports range lookup; `free_space_bytes` supports largest/suitable-size lookup.
- `btrfs_free_space_ctl::discardable_extents` and `discardable_bytes` keep current/previous discard statistics.
- `btrfs_free_space_ctl::cache_writeout_mutex` protects writeout from concurrent trim bitmap/range mutation.
- `btrfs_io_ctl::pages`, `cur`, `orig`, `index`, `num_pages`, `entries`, and `bitmaps` describe cache inode IO state.

Inline helpers:
- `btrfs_free_space_trimmed()` and `btrfs_free_space_trimming_bitmap()` classify trim state.
- `btrfs_trim_interrupted()` stops long trims on fatal signals or freezer activity.

API surface:
- Slab lifecycle: `btrfs_free_space_init()` and `btrfs_free_space_exit()`.
- Space-cache inode management: lookup, create, remove, truncate, load, write, and wait-for-cache-IO functions.
- Live free-space management: initialize a control, add/remove space, discard cache contents, dump state, check if trimmed, and allocate ranges.
- Cluster management: initialize clusters, find a cluster, allocate from one, and return cluster contents to the block group.
- Discard management: trim whole block groups, trim extent or bitmap phases separately, and handle fully remapped block group trim.
- Space-cache v1 activation: `btrfs_free_space_cache_v1_active()` and `btrfs_set_free_space_cache_v1_active()`.
- Sanity-test hooks can inject exact extent or bitmap entries and check whether a range exists.

This header is the contract between block group setup, extent allocation, discard workers, transaction cache writeout, and Btrfs free-space cache tests.
