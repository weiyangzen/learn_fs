# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_logmgr.c

## Role

Implements the JFS log manager: journal opening, initialization, append-only log record writing, group commit, sync-point advancement, log buffer I/O, log shutdown, and formatting.

## Main Responsibilities

- `lmLog()` serializes log writes per log, updates metapage and transaction recovery LSNs, writes a record, and advances sync points when the log crosses `nextsync`.
- `lmWriteRecord()` packs line-vector data plus `struct lrd` descriptors into 4 KiB log pages, splitting across pages as needed.
- `lmNextPage()` finalizes full pages, queues them for writeback, allocates the next circular log page, and updates log page sequence numbers.
- `lmGroupCommit()`, `lmGCwrite()`, and `lmPostGC()` group transactions with commit records on the same log page, write that page, wake waiters, and hand lazy commits to the transaction manager.
- `lmLogOpen()` supports shared external journals, inline journals, and a dummy no-integrity journal.
- `lmLogInit()` validates the log superblock, requires `LOGREDONE`, writes an initial `LOG_SYNCPT`, marks the log `LOGMOUNT`, and initializes log buffer state.
- `lmLogShutdown()` flushes outstanding work, writes a final sync point, marks the log `LOGREDONE`, records the final LSN, and tears down private log buffers.
- `jfs_flush_journal()` forces pending commit records and, for full waits, also pushes metadata and waits for `cqueue` and `synclist` drainage.
- `lmLogFormat()` initializes log superblock and data pages with sequence numbers arranged for circular log-end discovery.

## Important State and Synchronization

- `LOG_LOCK(log)` serializes append writes and sync-point updates.
- `LOGGC_LOCK(log)` protects group commit queues and transaction commit state.
- `LOGSYNC_LOCK(log)` protects the log sync list shared by metapages and tblocks.
- `jfs_log_mutex` protects global external-journal discovery and `dummy_log`.
- `jfsLCacheLock` protects the private `lbuf` free list and write queue.
- `log_redrive_list` plus `jfsIOWait()` moves deferred log I/O out of interrupt context.

## Interactions

- Consumes `struct tblock`, `struct tlock`, and `struct metapage` state from `jfs_txnmgr.c` and `jfs_metapage.c`.
- Calls `write_special_inodes()` over all superblocks sharing a journal to flush map/direct-inode metadata before sync points.
- Updates log active filesystem UUID slots in `struct logsuper` through `lmLogFileSystem()`.
- Calls `txLazyUnlock()` for non-forced transactions after commit records reach disk.

## Recovery and Integrity Notes

- The log requires `logredo` to have marked the journal `LOGREDONE` before normal open.
- `LOG_SYNCPT` records establish safe replay boundaries.
- Partial-page group commit writes leave the buffer queued until full-page write or explicit redrive.
- `JFS_NOINTEGRITY` still exercises journal state but bypasses disk I/O by completing bios directly.
