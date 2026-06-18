# File Research: sources/os/linux/linux/fs/xfs/xfs_inode_item.c

Implements the XFS inode log item: transaction precommit handling, log vector sizing/formatting, inode pin/unpin, AIL pushing, commit sequence tracking, flush completion, flush abort, and log-format conversion.

Key elements:
- Defines `xfs_ili_cache`, `INODE_ITEM`, inode log item sort key by inode number, and optional expensive precommit verification.
- Precommit updates VFS dirty-time state, upgrades eligible inodes to bigtime, fixes bad realtime extent-size hints, attaches/holds the inode cluster buffer late in transaction ordering, stores dirty flags, converts iversion logging to core logging, and merges last-flushed fields back into current fields.
- Late buffer attachment preserves AGI/AGF/inode-cluster lock ordering and ensures dirty inodes keep their backing buffer in memory while journaled.
- Size calculation accounts for log format, log dinode core, data fork extents/btree/local data, and attr fork extents/btree/local data.
- Formatting emits a 64-bit inode log format, log dinode core, and optional fork payloads while clearing incompatible/empty log field bits to avoid stale or uninitialized log data.
- Log dinode conversion handles bigtime vs legacy timestamps, legacy DMAPI field preservation, large extent counters, v3 inode fields, metatype, uuid, LSN, crc placeholder, and v2 flushiter.
- Pin/unpin increments/decrements inode pin counts and clears fsync/datasync commit sequences when the last pin drops.
- AIL push tries to flush the inode cluster buffer, returns pinned/flushing/locked states as appropriate, and queues flushed buffers for delayed write.
- Commit handling records commit and datasync sequence numbers before release and bypasses AIL insertion for stale inodes.
- Flush completion removes successfully written inode items from the AIL when LSNs match, clears failed bits, finishes flush state, detaches clean items from buffers, and drops buffer references.
- Abort paths remove inode items from AIL, clear flush/log fields, detach from buffers, handle shutdown from contexts without the cluster buffer locked, and release buffer references safely.
- Provides conversion from old 32-bit inode log format records to the native 64-bit structure for recovery.

Dependencies:
- Integrates with XFS transaction item ops, CIL/AIL, inode flush code in `xfs_inode.c`, buffer items, log recovery format definitions, VFS inode timestamps/versioning, realtime extent helpers, and shutdown/error handling.

Research notes:
- The `ili_fields`/`ili_last_fields` protocol prevents relogging from dropping data before a prior flush reaches disk.
- Inode items must keep a valid buffer pointer while in the AIL so push operations can locate the cluster buffer.
- Stale inode commit handling avoids inserting clean stale inodes into the AIL, which would otherwise persist until reclaim assertions fire.
