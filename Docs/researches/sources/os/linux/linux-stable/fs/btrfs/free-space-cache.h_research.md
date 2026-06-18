# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.h

## Purpose

Declares the runtime free-space cache v1 data structures, trim-state model, cache inode I/O context, and public APIs implemented by `free-space-cache.c`. This header is the interface used by block-group caching, allocation, discard, transaction writeout, and sanity-test code.

## Key Types

- `enum btrfs_trim_state`: distinguishes untrimmed, trimmed, and in-progress bitmap trimming states. `BTRFS_TRIM_STATE_TRIMMING` is bitmap-specific and allows long bitmap trim passes to preserve state.
- `struct btrfs_free_space`: one free-space extent or bitmap entry, indexed by offset and size rbtrees, with offset/bytes/max extent size, optional bitmap pointer, list hook, trim state, and bitmap extent count.
- `struct btrfs_free_space_ctl`: per-block-group controller containing free-space rbtrees, counters, bitmap thresholds, discardable statistics, block-group backpointer, writeout mutex, and active trimming ranges.
- `struct btrfs_free_space_op`: policy hook for deciding whether an extent should be represented as a bitmap.
- `struct btrfs_io_ctl`: transient page-walking state for reading/writing cache inodes.

## Public API Surface

The header exposes initialization/teardown, cache-inode lookup/create/remove/truncate, cache load/write/wait, runtime free-space add/remove/query/allocation, cluster setup/allocation/return, discard trimming entry points, remapped block-group trimming, v1 activation toggling, and test-only insertion/query helpers.

## Inline Helpers

`btrfs_free_space_trimmed()` and `btrfs_free_space_trimming_bitmap()` classify trim state. `btrfs_trim_interrupted()` provides a common trim cancellation predicate using fatal signals and freezer state.

## Integration Notes

The header includes `fs.h` because `struct btrfs_free_cluster` and other Btrfs-wide types are part of the public free-space interface. Consumers must respect the locking documented implicitly by the implementation: most operations acquire internal locks, but cluster return/allocation and cache writeout participate in block-group and transaction locking.
