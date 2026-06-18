# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.h

## Purpose

Defines ordered extent data structures, flags, and APIs.

## Main Contents

- `struct btrfs_ordered_sum` for queued checksum ranges.
- Ordered extent status flags: I/O done, complete, error, truncated, logged, logged csum, pending.
- Ordered extent type flags: regular, nocow, prealloc, compressed, encoded, direct.
- `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS` masks.
- `struct btrfs_ordered_extent`, containing file extent fields, state flags, qgroup reservation, refs, inode pointer, checksum/log/root/work lists, rb node, waits, and completion.
- `struct btrfs_file_extent`, mirroring file extent item details needed to allocate ordered extents.
- APIs for allocation, reference release, removal, finish/mark completion, lookup, wait, range lock/flush, splitting, error marking, and slab init/exit.

## Key Contract

The flags encode both lifecycle state and extent type. Callers creating ordered extents must pass exactly one exclusive type and respect direct/encoded/compressed compatibility rules enforced in `ordered-data.c`.
