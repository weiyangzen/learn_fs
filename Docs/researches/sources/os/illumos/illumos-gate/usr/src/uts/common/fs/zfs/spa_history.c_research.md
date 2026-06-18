# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_history.c

This file manages the pool history log, stored as a DMU object containing repeated little-endian record length plus packed nvlist records. The log behaves as a ring buffer while preserving the original pool creation command.

Key behavior:
- The history object bonus buffer is `spa_history_phys_t`, tracking physical max offset, logical BOF/EOF, preserved create-record length, and lost-record count.
- `spa_history_create_obj()` allocates the history object, adds it to `DMU_POOL_HISTORY`, and sizes the log to 0.1% of normal-class dspace, capped at 1 GiB and floored at 128 KiB.
- `spa_history_log_to_phys()` maps logical offsets to ring-buffer physical offsets after the preserved create region.
- `spa_history_advance_bof()` reads the next record length at BOF, advances BOF past that record, and increments `sh_records_lost`.
- `spa_history_write()` makes room by advancing BOF as needed, writes with wraparound, and advances EOF.
- `spa_history_log_notify()` converts selected history nvlist fields into normalized sysevent fields and posts `ESC_ZFS_HISTORY_EVENT`.
- `spa_history_log_sync()` creates the object lazily for older pools, adds timestamp and host, emits debug messages, posts internal history sysevents, packs the nvlist, writes length and record, and records the first command as the permanent create record.
- `spa_history_log()` wraps a command string; `spa_history_log_nvl()` sanitizes hidden args from input nvlist, adds zone and uid, and schedules async sync work.
- `spa_history_get()` reads command history chunks, waits for sync on first read when writeable, handles preserved-create reads, clamps overwritten offsets to BOF, and handles ring wraparound.
- `spa_history_log_internal()`, `_ds()`, and `_dd()` log internal TXG events, optionally tied to datasets or directories.
- `spa_history_log_version()` records pool/software/ZPL/UTS version information.

Important invariants:
- `spa_history_lock` protects ring offsets and writes.
- The first `ZPOOL_HIST_CMD` record is never overwritten.
- Internal events in syncing context write immediately; otherwise they schedule a sync task.
