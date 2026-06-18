# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4.c

Public/ext4 service API layer for the 9front `ext4srv` implementation. It exposes mount/unmount, journal start/stop/recovery, transactions, file open/read/write/truncate/seek/remove/link/rename, metadata get/set, symlink/mknod support, recursive directory removal, directory creation/opening, and directory iteration.

Key behavior:
- Defines Plan 9-style global error strings and mountpoint locking macros wrapping optional OS locks.
- `ext4_mount` initializes CRC32C tables, the block device, filesystem superblock state, logical block size, and block cache.
- `ext4_umount` finalizes filesystem state, cleans/flashes cache, tears down block device state, and clears the mount’s filesystem pointer.
- `ext4_journal_start`, `ext4_journal_stop`, `ext4_recover`, `ext4_trans_start`, `ext4_trans_stop`, and `ext4_trans_abort` bridge normal file operations to the local JBD implementation when the filesystem has a journal.
- `ext4_generic_open2` is the central pathname walker and creator. It descends from the root inode, validates file type expectations, creates missing intermediate directories for `O_CREAT`, truncates regular files for `O_TRUNC`, and fills `ext4_file` state.
- `ext4_link`, `ext4_unlink`, `ext4_create_hardlink`, and `ext4_remove_orig_reference` maintain directory entries, `.`/`..`, htree parent pointers, and link counts.
- `ext4_fread` and `ext4_fwrite` translate file offsets to filesystem blocks, coalesce contiguous block IO, handle short inline symlinks, update positions/counts, and update inode size and mtime on writes.
- Directory operations use `ext4_dir_iter` and the lower directory layer; recursive removal walks depth-first, truncates entries, unlinks them, and frees inodes.

Notable dependencies:
- Core local modules: `ext4_fs`, `ext4_dir`, `ext4_dir_idx`, `ext4_inode`, `ext4_super`, `ext4_block_group`, `ext4_trans`, `ext4_journal`, `ext4_crc32`.
- Plan 9 runtime assumptions appear through `werrstr`, `time(nil)`, `utfrrune`, and Plan 9 error/style conventions.

Research notes:
- This is the main API surface consumed by `ext4srv.c` and related Plan 9 service glue.
- Read-only checks are mostly done at public mutation entry points and creation paths.
- The implementation intentionally does not support file growth through truncate; `ext4_ftruncate_no_lock` returns “space preallocation not supported” when requested size is greater than or equal to current size.
- `ext4_fread` handles sparse holes for an initial unaligned read, but the full-block coalescing path and final partial-block path do not consistently check `fblock == 0`; sparse full-block or trailing reads can read physical block 0 instead of zero-filling.
- `ext4_fwrite` contains an explicit FIXME around partial failure after append allocation. It may update inode size after a short write but leaves nuanced error reporting around `rr` suppressed.
- Several metadata getters open an `ext4_file` only to obtain an inode number and do not call `ext4_fclose`; since `ext4_fclose` only clears local fields, this is not a disk resource leak, but it is an API-state inconsistency.
