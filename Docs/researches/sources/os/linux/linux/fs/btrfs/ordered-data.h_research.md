# File Research: sources/os/linux/linux/fs/btrfs/ordered-data.h

This header defines Btrfs ordered extent data structures, flags, and public APIs.

Key structures:
- `struct btrfs_ordered_sum` stores a logical checksum range and flexible checksum array.
- `struct btrfs_file_extent` captures target file extent item details for write setup.
- `struct btrfs_ordered_extent` records a pending write range, corresponding disk extent fields, bytes left, truncation state, flags, compression type, qgroup reservation, refs, inode pointer, checksum/log/root lists, waitqueue, rbtree node, work items, completion, and bio-context list.

Flags:
- Status bits include `BTRFS_ORDERED_IO_DONE`, `BTRFS_ORDERED_COMPLETE`, `BTRFS_ORDERED_IOERR`, `BTRFS_ORDERED_TRUNCATED`, `BTRFS_ORDERED_LOGGED`, `BTRFS_ORDERED_LOGGED_CSUM`, and `BTRFS_ORDERED_PENDING`.
- Exclusive type bits are `BTRFS_ORDERED_REGULAR`, `BTRFS_ORDERED_NOCOW`, `BTRFS_ORDERED_PREALLOC`, and `BTRFS_ORDERED_COMPRESSED`.
- Extra modifiers are `BTRFS_ORDERED_ENCODED` and `BTRFS_ORDERED_DIRECT`.
- `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS` define valid creation masks.

Exported API groups:
- Completion/removal: `btrfs_finish_one_ordered()`, `btrfs_finish_ordered_io()`, `btrfs_finish_ordered_extent()`, `btrfs_mark_ordered_io_finished()`, `btrfs_dec_test_ordered_pending()`, `btrfs_remove_ordered_extent()`, and `btrfs_put_ordered_extent()`.
- Allocation/checksums: `btrfs_alloc_ordered_extent()` and `btrfs_add_ordered_sum()`.
- Lookup/logging: ordered extent lookup by offset/range/first range and `btrfs_get_ordered_extents_for_logging()`.
- Waiting/flushing: `btrfs_start_ordered_extent_nowriteback()`, inline `btrfs_start_ordered_extent()`, `btrfs_wait_ordered_range()`, `btrfs_wait_ordered_extents()`, and `btrfs_wait_ordered_roots()`.
- Range locking: `btrfs_lock_and_flush_ordered_range()` and `btrfs_try_lock_ordered_range()`.
- Split/error/lifecycle: `btrfs_split_ordered_extent()`, `btrfs_mark_ordered_extent_error()`, `ordered_data_init()`, and `ordered_data_exit()`.

Design notes:
- The header documents the semantic difference between data I/O done and ordered extent complete.
- Ordered extents act as the bridge between writeback/direct I/O completion and eventual file extent/checksum metadata insertion.
