# File Research: sources/os/linux/linux/fs/btrfs/file.h

Public Btrfs regular-file operation interface. This header declares the VFS file operations table and the main regular-file helpers implemented by `file.c` and used by inode, direct I/O, encoded I/O, ioctl, reflink, logging, and writeback paths.

Key responsibilities:
- Exposes `btrfs_file_operations` for regular-file VFS registration.
- Declares `btrfs_sync_file()` for fsync and directory sync through tree logging or transaction commit.
- Declares file extent mutation APIs: `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, and `btrfs_mark_extent_written()`.
- Declares common write dispatch through `btrfs_do_write_iter()`, with optional encoded I/O arguments.
- Declares file release cleanup through `btrfs_release_file()`.
- Declares `btrfs_dirty_folio()` for marking copied page-cache data as delalloc and dirty.
- Declares `btrfs_fdatawrite_range()` for writeback with Btrfs compression-specific handling.
- Declares NOCOW check/lock and unlock helpers.
- Declares `btrfs_find_delalloc_in_range()` for discovering dirty or ordered ranges before file extent items exist.
- Declares `btrfs_write_check()` and `btrfs_buffered_write()` for shared write validation and buffered write entry.

Dependencies:
- Includes Linux basic type definitions.
- Forward-declares VFS file/inode/kiocb/iov_iter/folio/page structures and Btrfs inode, root, path, transaction, drop-extents, replace-extent, and encoded I/O structures.

Important invariants:
- A positive `btrfs_check_nocow_lock()` result means the caller owns the root snapshot write lock and must call `btrfs_check_nocow_unlock()`.
- `btrfs_replace_file_extents()` expects the target range and inode to already be locked by the caller and returns a transaction handle through `trans_out` on success.
- `btrfs_drop_extents()` behavior is controlled by caller-supplied `struct btrfs_drop_extents_args`, including path ownership, replacement mode, cache dropping, extent item size, and byte accounting.
- `btrfs_dirty_folio()` assumes the folio covers the written byte range and updates both Btrfs extent state and folio state.

Notable risks:
- This header exposes low-level file extent mutation functions whose correctness depends on external locking and transaction context.
- The write helpers mix VFS-facing and Btrfs-internal contracts; prototype changes must stay synchronized with direct I/O, encoded I/O, ioctl, and inode callers.
- Misuse of the NOCOW lock helpers can leave the snapshot lock held or permit unsafe writes into shared or snapshotted extents.
