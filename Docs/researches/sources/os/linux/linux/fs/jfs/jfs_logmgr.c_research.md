# File Research: sources/os/linux/linux/fs/jfs/jfs_logmgr.c

Implements the JFS journal/log manager: log record packing, log page rollover, group commit, syncpoint advancement, log open/close/format, and private log-buffer I/O. It coordinates tightly with `jfs_txnmgr.c`, `jfs_metapage.c`, and recovery code via the on-disk log structures from `jfs_logmgr.h`.

Key entry points:
- `lmLog()` serializes log writes, attaches metapages and transaction blocks to the log sync list, writes one logical log record, and triggers `lmLogSync()` when the next sync threshold is crossed.
- `lmWriteRecord()` copies changed metadata ranges from tlocks into current log pages, appends an `lrd` descriptor, handles cross-page records, and queues COMMIT records for group commit.
- `lmNextPage()` finalizes/writes the current log page and allocates/initializes the next circular log page.
- `lmGroupCommit()`, `lmGCwrite()`, and `lmPostGC()` batch transactions whose COMMIT records share a log page, submit the page, wake synchronous waiters, or hand lazy commits to `txLazyUnlock()`.
- `jfs_syncpt()` and `lmLogSync()` flush special metadata inodes, compute the oldest unresolved logsync item, write `LOG_SYNCPT`, and enforce `log_SYNCBARRIER` when the log gets too full.
- `lmLogOpen()`, `open_inline_log()`, and `open_dummy_log()` open external, inline, or no-integrity logs. External logs are shared through `jfs_external_logs` and UUID-checked.
- `lmLogInit()` validates the log superblock, opens append mode at the recovered end, writes an initial syncpoint, marks the log mounted, and initializes sync/group-commit state.
- `lmLogClose()` and `lmLogShutdown()` flush outstanding journal work, mark the log clean, update the log superblock, and tear down buffers.
- `lmLogFormat()` writes a new log superblock and initializes circular log pages.
- `jfs_flush_journal()` forces queued commit records through the group commit path and can wait until all log and logsync work drains.
- `jfsIOWait()` is the kernel thread redriving log buffers that cannot be submitted from completion/interrupt-sensitive paths.

Important state and synchronization:
- `LOG_LOCK` serializes append-side log writes.
- `LOGGC_LOCK` protects the commit queue and group commit flags.
- `LOGSYNC_LOCK` protects `synclist`, metapage/tblock LSN state, and syncpoint advancement.
- `jfsLCacheLock` protects lbuf free/write queue state.
- `log_redrive_list` is a global redrive queue consumed by `jfsIOthread`.

Log buffer manager details:
- Each log owns preallocated `lbuf` buffers backed by pages, avoiding page-cache allocation deadlocks during journal activity.
- `lbmWrite()` maintains a circular FIFO write queue per log and submits only the head.
- `lbmIODone()` updates committed LSN, removes released buffers, redrives the next queued page, runs group-commit completion, and wakes synchronous waiters.
- `no_integrity` mode still runs journaling logic but bypasses actual block I/O by directly completing bios.

Risks and invariants:
- Correctness depends on strict ordering between COMMIT record write, group-commit completion, map updates, and metapage `homeok`.
- `lmPostGC()` may run from I/O completion context, so it carefully avoids blocking and redrives later work through `jfsIOthread`.
- Log wrap pressure activates a sync barrier; transactions must drain before new work resumes.
- Shared external journals rely on UUID and active filesystem slots in the log superblock.
