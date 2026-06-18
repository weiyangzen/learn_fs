# File Research: sources/os/linux/linux/fs/jfs/jfs_logmgr.h

Defines the JFS journal on-disk formats, in-memory log state, log-buffer state, and log manager public API.

Core definitions:
- Log page size is fixed at `LOGPSIZE` 4096 bytes with `LOGPAGES` preallocated in-memory buffers per mounted filesystem.
- `struct logsuper` is the log superblock at page/block 1. It stores magic/version, state, size, block size, end LSN, log UUID, label, and up to `MAX_ACTIVE` filesystem UUIDs sharing an external journal.
- `struct logpage` is the journal data page layout: header, data area, and trailer. Header/trailer duplicate page sequence and EOR for recovery validation.
- `struct lrd` is the fixed-size log record descriptor placed after variable-length record data. It covers `LOG_COMMIT`, `LOG_SYNCPT`, `LOG_MOUNT`, redo/noredo page records, inode extent filters, and map update records.
- `struct lvd` describes logged line-vector data ranges.

In-memory structures:
- `struct jfs_log` contains active superblocks, journal block device file, circular log cursor, current lbuf, write lock, syncpoint fields, group-commit queue, sync list, write queue, UUID, and no-integrity flag.
- `struct lbuf` is a private log I/O buffer with queue links, page pointer, page offset, log page number, EOR/committed EOR, disk block, and completion wait queue.
- `struct logsyncblk` is the common prefix used by metapages and transaction blocks so both can be linked into `jfs_log.synclist`.

Flags and macros:
- Log flags include inline log, sync barrier, quiesce, and flush.
- Group commit flags describe queued, ready, committed, end-of-page, lazy, and error states.
- `logdiff()` computes circular distance from the current syncpoint.

Exports:
- Lifecycle: `lmLogOpen`, `lmLogClose`, `lmLogInit`, `lmLogShutdown`, `lmLogFormat`.
- Runtime: `lmGroupCommit`, `jfs_flush_journal`, `jfs_syncpt`, `jfsIOWait`.
