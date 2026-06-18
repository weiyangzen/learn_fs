# sources/storage-engines/wiredtiger/src/conn/conn_compact.c

## Purpose
This file implements the background compaction server. It tracks per-file compaction outcomes, processes include/exclude eligibility from `WT_SESSION::compact` configuration, walks metadata for `file:` entries, avoids compaction under cache pressure, and runs compaction in a dedicated connection server thread.

## Important APIs, Types, and Functions
`__wti_background_compact_server_create` and `__wti_background_compact_server_destroy` own the server thread, internal session, condition variable, stat hash, and exclude hash. `__wt_background_compact_signal` is the API path that enables or disables background compaction, validates `background`, `run_once`, and `exclude`, prevents reconfiguration while already running, updates `conn->background_compact.config`, and signals the server.

`__background_compact_exclude_list_process`, `__background_compact_exclude_list_add`, `__background_compact_exclude_list_clear`, and `__background_compact_exclude` maintain an exclude hash keyed by table name without the `table:` prefix and checked against `file:` URIs. `__background_compact_get_stat`, `__background_compact_list_insert`, `__background_compact_list_remove`, and `__background_compact_list_cleanup` maintain `WT_BACKGROUND_COMPACT_STAT` entries keyed by file URI and file id.

`__wt_background_compact_start` and `__wt_background_compact_end` are called around actual compact operations to record starting size, ending size, bytes rewritten, success/failure, bytes recovered, and the moving average used by skip heuristics. `__background_compact_find_next_uri` scans the metadata table from the last URI and chooses the next eligible `file:` URI. `__background_compact_server` runs the main loop.

## Control Flow and Behavior
Server creation is skipped for in-memory, read-only, and disaggregated connections. Otherwise the connection allocates per-bucket `stat_hash` and `exclude_list_hash`, opens an internal `compact-server` session with `WT_SESSION_CAN_WAIT | WT_SESSION_IGNORE_CACHE_SIZE`, allocates the condition, and starts the thread.

`__wt_background_compact_signal` serializes commands with `background_compact.lock`. It rejects a new command while a prior signal is pending, rejects background compaction for in-memory/read-only databases, strips `background=` from the config so only real compact options are compared, and refuses config changes while already running. On enable it stores `run_once` and rebuilds the exclude list. It toggles the atomic `running` flag, stores the stripped config, sets `signalled`, and wakes the thread.

The server loop remembers the current metadata URI scan position. When disabled, after a full iteration, or under cache pressure, it waits for the configured full-iteration interval and resets the scan to `file:` when beginning a new pass. While running, it checks dirty and clean eviction pressure before doing work. It then finds the next eligible `file:` metadata entry, copies the latest config under lock, and invokes `WT_SESSION::compact` on that file. `EBUSY`, `ENOENT`, `ETIMEDOUT`, `WT_ROLLBACK`, and interruption `WT_ERROR` from a disabled server are treated as nonfatal background outcomes; other errors panic the connection.

## State and Persistence Behavior
The server's durable inputs are metadata table entries and file sizes. Its own state is in-memory: the scan cursor URI, tracked file stats, skip counts, `bytes_rewritten_ema`, `files_compacted`, `files_skipped`, exclude hash, config string, and `running/run_once/signalled` flags. Tracked stat entries are reset when a file id changes, which handles drop-and-recreate of the same URI. Entries are also removed on disable, exit, or when idle longer than `max_file_idle_time`.

The compaction operation itself rewrites block-manager state and may reclaim file space. This file records the before/after sizes and updates background compaction stats, but compaction persistence is provided by the lower block manager and metadata layers.

## Dependencies and Integration Points
This code depends on metadata cursors, read-uncommitted metadata traversal, `__wt_compact_check_eligibility`, block manager named-size checks, btree file ids, WT compact APIs, connection stats, internal sessions, condition variables, and cache pressure helpers `__wt_evict_dirty_needed`, `__wt_evict_clean_needed`, and `__wt_evict_cache_stuck`.

It integrates with public `WT_SESSION::compact` background mode, `debug_mode=(background_compact)`, format's background compact workload, and csuite tests such as `wt8246_compact_rts_data_correctness`.

## Risks
Metadata traversal is explicitly called out as temporary until a dedicated internal API exists. It uses read-uncommitted scans and loops to avoid returning a key less than or equal to the previous URI; changes here can miss files, loop incorrectly, or compact stale metadata. Exclude entries are specified as `table:` URIs but matched against derived `file:` table names, so naming assumptions matter.

The server avoids cache pressure but compaction can still race with file drops, permission changes, checkpoints, rollback, and application load. The skip heuristic depends on file id, previous success, bytes rewritten EMA, `max_file_skip_time`, and file size; mistakes can cause either too much compaction or starvation. Signal handling must preserve the invariant that a running config cannot be changed in place.

## Test Signals
Useful signals include `background_compact_running`, `background_compact_success`, `background_compact_fail`, `background_compact_timeout`, `background_compact_interrupted`, skip counters for small files, no-such-file, permission, exclude, unsuccessful files, bytes recovered, EMA, and tracked file count. Format workload toggles background compaction, and csuite foreground/background compaction tests check data correctness across rollback-to-stable and compaction. Tests should cover run-once full iteration completion, exclude validation rejecting non-`table:` URIs, disable while compact is active, and drop/recreate id changes.
