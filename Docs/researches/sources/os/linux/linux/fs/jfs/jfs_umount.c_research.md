# File Research: sources/os/linux/linux/fs/jfs/jfs_umount.c

Implements full unmount and read-write-to-read-only unmount handling for JFS.

`jfs_umount()`:
- Flushes outstanding journal work with `jfs_flush_journal(log, 2)` when mounted read-write.
- Takes `LOG_LOCK` while clearing special inode pointers so `write_special_inodes()` in the log sync path cannot see partially torn-down `sbi` state.
- Unmounts and frees the fileset inode map, secondary aggregate inode map, primary aggregate inode map, and block map.
- Flushes direct metadata mapping pages before marking the filesystem clean.
- Calls `updateSuper(sb, FM_CLEAN)` and `lmLogClose()` when a log is active.

`jfs_umount_rw()`:
- Used when remounting read-only from read-write.
- Flushes the journal, syncs block and inode maps, writes all direct metadata pages, marks the superblock clean, and closes the log.

Important invariant:
- Metadata home writes must reach disk before the superblock is marked clean and before the filesystem is removed from the active journal list.
