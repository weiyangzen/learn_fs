# File Research: sources/local-fs/kdave-linux/fs/btrfs/file.h

Public Btrfs regular-file operation interface. This header declares the exported file operation table and the file write, fsync, extent mutation, dirtying, NOCOW, delalloc search, and writeback helpers implemented by `file.c`.

Key responsibilities:
- Exposes `btrfs_file_operations` for regular-file VFS registration.
- Declares fsync via `btrfs_sync_file()`.
- Declares extent dropping and replacement APIs: `btrfs_drop_extents()` and `btrfs_replace_file_extents()`.
- Declares `btrfs_mark_extent_written()` for converting prealloc ranges to regular written file extents.
- Declares `btrfs_do_write_iter()` for common write dispatch, including optional encoded writes.
- Declares file release cleanup through `btrfs_release_file()`.
- Declares `btrfs_dirty_folio()` for marking copied page-cache data as delalloc and dirty.
- Declares range writeback helper `btrfs_fdatawrite_range()`.
- Declares NOCOW range probe/lock and unlock helpers.
- Declares delalloc range discovery used by seek/logging-style callers.
- Declares write validation and buffered write entry points.

Dependencies:
- Includes Linux basic type definitions.
- Forward-declares VFS structures, folios/pages, iov_iter/kiocb, Btrfs inode/root/path/transaction, encoded I/O args, drop-extents args, and replace-extent info.

Important invariants:
- `btrfs_check_nocow_lock()` callers must call `btrfs_check_nocow_unlock()` when the function returns a positive result.
- `btrfs_replace_file_extents()` expects a previously locked range and returns a transaction handle through `trans_out` on success.
- `btrfs_drop_extents()` behavior is controlled by the caller-supplied `struct btrfs_drop_extents_args`, including path ownership, replacement mode, cache dropping, and accounting output.

Notable risks:
- This header exposes low-level extent mutation entry points; misuse outside the expected inode lock, mmap lock, extent lock, and transaction contexts can corrupt file extent state.
- The write helpers mix VFS-facing and Btrfs-internal contracts, so changes in direct/encoded/buffered write dispatch must keep prototypes synchronized across the file, ioctl, and direct I/O code.
