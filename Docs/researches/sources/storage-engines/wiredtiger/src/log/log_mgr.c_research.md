# sources/storage-engines/wiredtiger/src/log/log_mgr.c

## Purpose
`log_mgr.c` owns lifecycle, configuration, compatibility-version policy, and background service threads for the WiredTiger log subsystem. It parses `log.*` and `transaction_sync.*` configuration, creates/destroys `WTI_LOG`, starts log server threads, drives idle force writes, file close/sync, write-LSN advancement, preallocation, and log removal.

## Important APIs and Functions
- `__wt_logmgr_config`: parse logging configuration, validate incompatibilities, set compressor/path/file size/prealloc/remove/zero-fill/recovery/sync options.
- `__wt_logmgr_create`: allocate and initialize `WTI_LOG`, locks, condition variables, version settings, open/create log files, initialize slots, and write a creation message before recovery.
- `__wt_logmgr_open`: start background log-close, write-LSN, and log-server threads after recovery.
- `__wt_logmgr_reconfig`: apply allowed runtime config and update log version policy.
- `__wt_logmgr_destroy`: stop threads, join them, destroy slots/handles/locks/conditions, and free manager-owned memory.
- `__wt_logmgr_compat_version`, `__logmgr_get_log_version`, `__logmgr_version`: map WiredTiger compatibility versions to log file versions and force live file rollover/removal for downgrade compatibility.
- `__wt_log_truncate_files`: public removal/truncation helper for manual or backup-driven removal.
- Background thread bodies:
  - `__log_file_server`: fsync/truncate/close old log file handles after rollover.
  - `__log_wrlsn_server`: calls `__wti_log_wrlsn` to advance `write_lsn` in contiguous slot order.
  - `__log_server`: forces idle buffers, preallocates future log files, and removes old logs.
- Removal/preallocation helpers: `__compute_min_lognum`, `__log_remove_once`, `__log_prealloc_once`, `__logmgr_force_remove`.

## Control Flow
Configuration:
1. `__wt_logmgr_config` reads `log.enabled`; rejects logging with `in_memory`.
2. On initial config, it resolves compressor and log path and fixed file size/extension settings.
3. If enabled, it parses removal/archive, dirty OS-cache percentage, preallocation, force-write wait, recovery mode, zero fill, and transaction sync mode.
4. Transaction sync flags are assembled locally and published with a release barrier.

Startup:
1. `__wt_logmgr_create` returns early if logging was not configured.
2. It sets `WT_LOG_ENABLED`, allocates `WTI_LOG`, initializes all LSNs/locks/conditions, applies version selection, opens/creates log files, initializes slots, and writes a system message.
3. `__wt_logmgr_open` sets the server flag, starts close/wrlsn/server sessions and threads, and writes a post-recovery startup message.

Runtime threads:
1. `__log_server` periodically forces buffered writes when idle, preallocates files under hot-backup constraints, and removes archived files when configured.
2. `__log_wrlsn_server` advances `write_lsn` by sorting written slots by release LSN and coalescing contiguous slots.
3. `__log_file_server` observes `log_close_fh`, waits for writes through `log_close_lsn`, fsyncs/truncates/closes the old file, then advances `sync_lsn` to the next file start.

Shutdown:
1. `__wt_logmgr_destroy` clears the log-server flag, signals/join threads, closes internal sessions, destroys slot buffers and file handles, destroys conditions/locks, and frees `log_path`/`log`.

## State and Persistence Behavior
- Manager flags distinguish configured, enabled, existing logs, removal, recovery dirty/done/error/failure, downgrade, forced downgrade, incremental backup requirements, and zero-fill policy.
- `req_min/req_max` store compatibility-required log versions and are checked before modifying files.
- Removal keeps all logs needed by checkpoint, sync, active/incremental backup, and debug retention.
- Preallocation adapts `log_mgr.prealloc`: missed files increase the target, surplus files gradually decrease it, while `prealloc_init_count` remains the configured baseline.
- The server writes log messages marking creation and thread startup, which become persistent message records.

## Dependencies and Integration Points
- Calls physical operations from `log.c` (`__wti_log_open`, `__wti_log_close`, `__wti_log_force_write`, `__wti_log_wrlsn`, `__wti_log_allocfile`, `__wti_log_remove`, `__wti_log_set_version`, `__wt_log_printf`, `__wt_log_truncate_files`).
- Interacts with connection open/close/reconfiguration, checkpoint sessions, hot backup locks, debug retention config, stats counters, internal sessions, and thread/condition APIs.
- Consumes compatibility version state from the connection and affects recovery/removal behavior through `WT_LOG_FORCE_DOWNGRADE`.

## Risks and Edge Cases
- Reconfiguration intentionally cannot enable/disable logging or change fixed settings like path/compressor/file size; accepting those changes would be unsafe.
- Thread shutdown ordering matters because checkpoint server may be gone while logging still tracks log-written thresholds.
- Removal must not race with open log cursors or hot backup; it uses `log_remove_lock`, cursor counts, and hot backup locks.
- Downgrade requires forcing a checkpoint and removal of newer-version logs; failures can leave logs incompatible with requested versions.
- Barrier semantics around `log_close_fh/log_close_lsn` are explicitly documented and TSAN-specific in places.
- `__logmgr_force_remove` opens an internal session and loops checkpoint/removal until old logs disappear; errors here can block compatibility downgrade.

## Test Signals
- Config tests for enabled mismatch on reconfigure, in-memory incompatibility, read-only plus zero-fill rejection, deprecated `log.archive`, and transaction sync mode flags.
- Lifecycle tests for create/open/destroy with logging enabled/disabled/read-only and for startup messages.
- Threaded stress tests for slot close, write-LSN advancement, file rollover, idle force writes, and shutdown with outstanding writes.
- Log archival tests for checkpoint/sync minima, backup cursor minima, debug retention, open log cursor blocking, and incremental backup removal.
- Compatibility tests for live downgrade, forced removal, and version bounds.
