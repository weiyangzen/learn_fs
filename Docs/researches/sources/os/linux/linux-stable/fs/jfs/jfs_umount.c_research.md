# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_umount.c

## Role

Implements full JFS unmount and read-write-to-read-only unmount paths.

## Main Responsibilities

- `jfs_umount()`:
  - Flushes outstanding journal transactions if a log exists.
  - Holds the log lock while clearing special inode pointers so `write_special_inodes()` cannot race through `log->sb_list`.
  - Unmounts and frees fileset imap, secondary aggregate imap, aggregate imap, and aggregate block map.
  - Waits for direct-inode metadata mapping writeback.
  - Marks the superblock clean and closes the log on read-write mounts.
- `jfs_umount_rw()`:
  - Flushes the journal.
  - Syncs block and inode maps.
  - Waits for direct-inode metadata writeback.
  - Updates the superblock to `FM_CLEAN`.
  - Closes the log.

## Important Interactions

- Uses `jfs_flush_journal`, `LOG_LOCK`, `updateSuper`, and `lmLogClose`.
- Uses `diUnmount`, `diFreeSpecial`, `dbUnmount`, `dbSync`, and `diSync`.
- Coordinates directly with log-manager metadata flushing over `log->sb_list`.

## Correctness Notes

The code ensures metadata reaches disk before marking the filesystem clean. It also protects against a race where log sync code could see partially cleared `jfs_sb_info` special inode pointers during unmount.
