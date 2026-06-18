# File Research: sources/os/linux/linux/fs/ext4/fsync.c

Implements ext4 `fsync` / `fdatasync` handling for journaled and non-journaled filesystems.

Key behavior:
- `ext4_sync_parent()` handles no-journal crash safety for newly created files by recursively syncing freshly created parent directories marked `EXT4_STATE_NEWENTRY`.
- `ext4_fsync_nojournal()`:
  - syncs metadata buffer lists without a flush
  - forces inode table writeout
  - syncs parent directories when required
  - requests a block-device flush when barriers are enabled
- `ext4_fsync_journal()`:
  - chooses `i_datasync_tid` for datasync or `i_sync_tid` for full fsync
  - forces a full commit for directories and special files because fast commits do not support those fsync targets
  - requests an extra flush if JBD2 barriers will not cover the transaction’s data barrier
  - invokes `ext4_fc_commit()` for regular-file journal fsync
- `ext4_sync_file()`:
  - rejects emergency state
  - handles read-only mounts as already synced
  - dispatches no-journal vs journal mode
  - writes and waits on the requested file range before journal commit
  - issues a final device flush when needed
  - reports writeback errors through `file_check_and_advance_wb_err()`

Important interactions:
- Regular-file fsync is the main entry point into ext4 fast commits.
- Non-regular journaled fsync deliberately falls back to full JBD2 commit.
- No-journal mode depends on metadata buffer lists and parent directory syncing to narrow crash-loss windows.
