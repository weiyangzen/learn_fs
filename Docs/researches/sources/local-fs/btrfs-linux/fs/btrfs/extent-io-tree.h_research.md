# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-io-tree.h

## Summary
Defines Btrfs extent-state bits, extent I/O tree ownership types, core extent-state structures, and public APIs for range state mutation, locking, and queries.

## Main Contents
- Extent state bits such as `EXTENT_DIRTY`, `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`, `EXTENT_DELALLOC`, `EXTENT_BOUNDARY`, `EXTENT_NODATASUM`, reservation/accounting bits, ordered-completion bits, and `EXTENT_NOWAIT`.
- Control masks: `EXTENT_DO_ACCOUNTING`, `EXTENT_CTLBITS`, `EXTENT_LOCK_BITS`.
- Device allocation aliases: `CHUNK_ALLOCATED`, `CHUNK_TRIMMED`, `CHUNK_STATE_MASK`.
- Tree owner enum values such as inode I/O, btree inode I/O, pinned extents, dirty transaction pages, log csum ranges, device allocation state, and selftests.
- `struct extent_io_tree`.
- `struct extent_state`.

## Key Interfaces
The header declares all extent-state lifecycle, lock, set/clear/convert, search, count, and test helpers implemented in `extent-io-tree.c`. It also provides inline convenience wrappers for normal extent locks, direct-I/O extent locks, dirty clearing, and unlocking.

## Important Details
`extent_io_tree` stores either `fs_info` or an owning `btrfs_inode` depending on `owner`. `owner == IO_TREE_INODE_IO` means the inode pointer is valid and `fs_info` is reached through `inode->root`.

`EXTENT_DELALLOC_NEW` has a narrow ownership rule: it must be cleared during ordered extent completion or on submission error paths that did not create ordered extents. Page release/invalidation must not clear it when ordered extents are in flight.

`EXTENT_ADD_INODE_BYTES` is a control flag used when clearing new delalloc after successful ordered completion so VFS inode byte accounting and Btrfs new-delalloc accounting change atomically.

## Risks
The bit definitions encode accounting contracts, not just range labels. Misusing `EXTENT_DO_ACCOUNTING`, `EXTENT_DELALLOC_NEW`, or `EXTENT_ADD_INODE_BYTES` can cause reservation leaks or incorrect stat data.

The device allocation tree reuses bit values under `CHUNK_*` aliases, so generic extent-state helpers must be used with awareness of the tree owner and bit meaning.
