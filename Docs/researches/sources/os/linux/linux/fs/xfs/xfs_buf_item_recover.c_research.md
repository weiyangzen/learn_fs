# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_item_recover.c

Implements log recovery for physical buffer log items. It performs two-pass cancel handling, validates recovered buffer types, replays dirty buffer regions, handles special inode/dquot/superblock cases, and manages the recovery cancel table.

Key behavior:
- Maintains a 64-bucket `l_buf_cancel_table` of cancelled buffer ranges so old freed metadata is not replayed into reused blocks.
- Pass 1 validates buffer log format iovecs and records `XFS_BLF_CANCEL` entries.
- Pass 2 skips cancelled buffers, reads target buffers, compares on-disk metadata LSNs against the log transaction LSN, and replays only when needed.
- `xlog_recover_validate_buf_type` maps logged buffer type flags and magic numbers to correct buffer verifier ops for writeback.
- Regular buffer recovery copies logged chunks according to the dirty bitmap.
- Inode buffer recovery only replays `di_next_unlinked` fields, because inode core data is logged separately.
- Dquot buffer recovery skips quota types disabled by recovered QUOTAOFF items.
- Primary superblock recovery updates in-core superblock, device size, per-AG, and realtime group state after growfs replay.

This file is safety-critical for crash recovery because it prevents stale metadata replay and ensures recovered buffers carry correct verifier/LSN state before delayed writeback.
