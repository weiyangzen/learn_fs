# File Research: sources/os/linux/linux/fs/xfs/xfs_inode_item_recover.c

## Role
Implements log recovery for inode log items. During pass 2 recovery it readaheads inode cluster buffers, replays logged inode cores and fork data into on-disk dinodes, handles old 32-bit inode log formats, validates recovered metadata, and queues modified buffers for delayed writeback.

## Main Structures and Entry Points
- `xlog_recover_inode_ra_pass2` starts inode-buffer readahead from the inode log format record, handling native and 32-bit log item formats.
- `xlog_recover_inode_commit_pass2` is the core replay function for `XFS_LI_INODE` items.
- `xfs_recover_inode_owner_change` reconstructs a minimal in-core inode during recovery to reparent BMBT owners after extent swap operations.
- `xfs_log_dinode_to_disk`, timestamp helpers, and extent-count helpers convert the logged dinode representation to on-disk endian format.
- `xlog_recover_inode_dbroot` converts logged data-fork root blocks for normal BMBT and realtime metadata btrees.
- `xlog_inode_item_ops` registers the recovery operations.

## Behavior
The replay path first converts old format items if needed, skips replay if the target inode buffer was canceled, reads the inode buffer, verifies both existing disk inode magic and logged dinode magic, and uses inode LSN/flushiter rules to avoid replaying stale records. It validates logged fork format, fork offset, extent counts, large extent-count feature compatibility, and logged dinode size before copying core fields and optional fork payloads.

For v3 inodes, recovery writes the current transaction LSN to the dinode instead of trusting the logged LSN. It copies device numbers for special files, converts logged data and attr fork payloads according to the log flags, recomputes CRCs, runs full dinode verification, marks the buffer as log-recovery modified, and queues it to the caller's delwri list.

## Interactions
This file depends on bmap btree conversion, realtime rmap/refcount btree conversion, buffer recovery cancellation, inode verifiers, and the log recovery item dispatcher. It is tightly coupled to `xfs_inode_item` log format flags and to fork owner change semantics used by extent swap.

## Invariants and Error Handling
- Recovered regular files must have extent, btree, or meta-btree data forks; directories must have extents, btree, or local data forks.
- Large extent counts require the filesystem feature and zero padding.
- Total data and attr extent counts cannot exceed inode block count.
- Fork offsets and logged dinode sizes are bounded by inode size expectations.
- Owner change replay is skipped for deleted inodes but still attempted when disk inode LSN is newer than the replay item.
- Corruption is reported with `XFS_CORRUPTION_ERROR`/`xfs_alert`, and failures return `-EFSCORRUPTED` or allocation/read errors.
