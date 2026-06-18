# File Research: sources/os/linux/linux-stable/fs/ext4/fsync.c

This file implements ext4’s fsync/fdatasync path for regular files and related metadata synchronization.

Major responsibilities:
- `ext4_sync_file()` is the VFS fsync entry point:
  - Rejects emergency state.
  - Asserts there is no current journal handle.
  - Skips work on read-only superblocks.
  - Handles no-journal and journaled modes separately.
  - Issues device flushes when barriers are required.
  - Reports and advances writeback errors.
- No-journal fsync:
  - `ext4_fsync_nojournal()` syncs metadata buffer-head tracking with `mmb_fsync_noflush()`, writes the inode table buffer through `ext4_write_inode()`, recursively syncs fresh parent directories when needed, and requests a barrier flush if mounted with barriers.
  - `ext4_sync_parent()` walks aliases/parents for inodes marked `EXT4_STATE_NEWENTRY`, syncing parent metadata buffers and inode metadata to close crash windows for just-created directory entries.
- Journaled fsync:
  - `ext4_fsync_journal()` chooses `i_datasync_tid` or `i_sync_tid`, forces a full commit for non-regular files, determines if a barrier flush is needed, and calls `ext4_fc_commit()` for the target transaction.

Important design points:
- Fast commit is used for regular-file fsync in journaled mode; directories and special files force a full commit.
- Data writeback is completed before journal commit via `file_write_and_wait_range()`.
- Barrier handling is split between JBD2 transaction behavior and explicit `blkdev_issue_flush()` when needed.
- No-journal mode must explicitly sync parent directories for recently created entries because there is no journal commit ordering to rely on.

Key invariants:
- `ext4_sync_file()` must not run inside an active ext4 journal handle.
- Writeback errors are reported even if the metadata/journal path succeeded.
- Parent sync recursion stops once `EXT4_STATE_NEWENTRY` is cleared or an error occurs.
