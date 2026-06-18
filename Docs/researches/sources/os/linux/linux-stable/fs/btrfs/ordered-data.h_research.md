# File Research: sources/os/linux/linux-stable/fs/btrfs/ordered-data.h

## Summary
Defines ordered extent structures, flags, file extent metadata, and public ordered-data APIs.

## Main Contents
- `struct btrfs_ordered_sum`.
- Ordered extent status/type flag enum.
- `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS`.
- `struct btrfs_ordered_extent`.
- `struct btrfs_file_extent`.
- Function declarations for allocation, lookup, finish, wait, split, error marking, and slab lifecycle.

## Important Details
Ordered extent flags include status bits (`IO_DONE`, `COMPLETE`, `IOERR`, `TRUNCATED`, `LOGGED`, `LOGGED_CSUM`, `PENDING`) and mutually exclusive type bits (`REGULAR`, `NOCOW`, `PREALLOC`, `COMPRESSED`). `ENCODED` is an extra compressed-write bit; `DIRECT` is an extra direct-I/O bit for regular/NOCOW/prealloc writes.

`struct btrfs_ordered_extent` mirrors file extent item fields such as file offset, logical length, RAM length, disk bytenr, disk length, and offset. It also stores bytes left, truncation length, compression type, qgroup reservation, inode pointer, checksums, logging linkage, rbtree node, root list node, work items, completion, and bio ordered-csum linkage.

## Risks
Only one exclusive type flag may be set. Mislabeling DIRECT, ENCODED, COMPRESSED, NOCOW, or PREALLOC changes completion, metadata insertion, qgroup release, and split behavior.
