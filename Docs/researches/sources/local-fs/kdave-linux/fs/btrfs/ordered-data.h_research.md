# File Research: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.h

## Purpose

`ordered-data.h` defines the ordered extent data model and declares the APIs implemented by `ordered-data.c`.

## Structures

`struct btrfs_ordered_sum` records checksum data for a logical range, with a variable-length `sums[]` tail.

`struct btrfs_ordered_extent` tracks one pending write extent. Key fields include file offset, logical length, on-disk bytenr/length, encoded extent metadata, remaining bytes, truncation length, flags, compression type, qgroup reservation, refcount, inode owner, checksum list, fsync log list, waitqueue, rb-tree node, root list node, work/completion state, and bio-context list.

`struct btrfs_file_extent` represents the file extent item target for a write, including disk range, logical length, ram length, offset, and compression.

## Flags

The ordered extent flag enum includes completion/error/logging state bits and mutually exclusive type bits:

- `BTRFS_ORDERED_REGULAR`
- `BTRFS_ORDERED_NOCOW`
- `BTRFS_ORDERED_PREALLOC`
- `BTRFS_ORDERED_COMPRESSED`

Additional modifiers include `BTRFS_ORDERED_ENCODED` and `BTRFS_ORDERED_DIRECT`. Static assertions ensure flags fit in `unsigned long`, and masks define exclusive/type flag groups.

## APIs

The header declares allocation, finish, wait, lookup, logging, range lock, split, error marking, and slab init/exit functions. `btrfs_start_ordered_extent()` is an inline wrapper around the no-writeback variant.

## Integration Notes

This header is central to Btrfs writeback, direct I/O, compression, fsync, transaction commit, qgroup accounting, and subvolume snapshot consistency. Flag invariants are important: only one exclusive type flag is valid, encoded implies compressed, and direct excludes compressed/encoded.
