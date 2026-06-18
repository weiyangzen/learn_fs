# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file.h

## Purpose

Declares the public Btrfs regular-file interface implemented by `file.c` and consumed by inode, direct IO, encoded IO, ioctl, reflink, mmap, logging, and writeback paths.

## Public API Surface

- `btrfs_file_operations` exports the VFS regular-file operations table.
- `btrfs_sync_file()` is the fsync entry point for files and directories.
- `btrfs_drop_extents()` removes or trims file extent items over a range.
- `btrfs_replace_file_extents()` replaces a locked file range with holes or supplied extent metadata.
- `btrfs_mark_extent_written()` converts preallocated file extent ranges to written regular extents.
- `btrfs_do_write_iter()` dispatches encoded, direct, and buffered writes.
- `btrfs_release_file()` frees Btrfs per-file private state and handles flush-on-close.
- `btrfs_dirty_folio()` marks a folio range as dirty/delalloc.
- `btrfs_fdatawrite_range()` starts writeback with Btrfs compression-aware retry behavior.
- `btrfs_check_nocow_lock()` and `btrfs_check_nocow_unlock()` expose NOCOW write eligibility and snapshot lock release.
- `btrfs_find_delalloc_in_range()` finds dirty or ordered delalloc ranges.
- `btrfs_write_check()` performs common Btrfs write preflight.
- `btrfs_buffered_write()` exposes the buffered write implementation.

## Dependencies And Consumers

The header forward-declares VFS, iterator, folio, extent-state, transaction, root, inode, drop-extents, replace-extent, and encoded-IO structures to keep includes light. It is the boundary between Btrfs regular file operations and other subsystems that need to mutate file extents, write data, or query delalloc state.

## Invariants And Risks

- Callers of extent mutation APIs must satisfy the locking and transaction expectations documented in `file.c`.
- `btrfs_check_nocow_lock()` has paired unlock semantics only when it returns success.
- `btrfs_replace_file_extents()` may return an open transaction through `trans_out`, so ownership transfer must be handled carefully.
- Delalloc range queries combine io-tree and ordered-extent state; callers should pass cached extent state only when it matches the current task/use context.
