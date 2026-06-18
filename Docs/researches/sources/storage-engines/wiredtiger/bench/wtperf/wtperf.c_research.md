# sources/storage-engines/wiredtiger/bench/wtperf/wtperf.c

## Purpose
`wtperf.c` is the executable driver for WiredTiger's `wtperf` benchmark. It parses command-line and file options, builds connection/table configuration strings, creates and populates benchmark tables, runs mixed workload threads, starts optional background backup/checkpoint/flush/scan/monitor activity, reports throughput and latency, and tears the database down when configured.

## Important APIs, Types, And Functions
The file operates around `WTPERF`, `WTPERF_THREAD`, `WORKLOAD`, and `TRACK` from `wtperf.h`. Key functions are `main`, `start_all_runs`, `start_run`, `execute_populate`, `execute_workload`, `worker`, `populate_thread`, `monitor`, `backup_worker`, `checkpoint_worker`, `flush_tier_worker`, `scan_worker`, `create_tables`, `create_uris`, `close_reopen`, `wtperf_rand`, and `run_mix_schedule`. It uses the WiredTiger C API heavily: `wiredtiger_open`, connection/session creation, cursors, transactions, checkpoints, backup cursors, `wiredtiger_calc_modify`, and session truncate.

## Control Flow
`main` initializes defaults, processes `-C`, `-h`, `-m`, `-O`, `-o`, and `-T`, appends derived connection/table config, validates with `config_sanity`, recreates homes when `create=true`, writes `CONFIG.wtperf`, then calls `start_all_runs`. A single database runs directly through `start_run`; multiple databases clone `WTPERF` and execute each home in a thread. `start_run` opens the connection, creates URIs/tables, optionally launches monitor, populates records, closes/reopens for workload isolation or readonly mode, starts background workers, runs `execute_workload`, prints final counters and latencies, and joins all helper threads.

## State And Persistence Behavior
Persistent state is the WiredTiger home directory, table data, optional backup directories, monitor output files, and `CONFIG.wtperf`. Shared in-memory state includes atomic insert/log counters, per-thread `TRACK` counters, volatile stop/error/activity flags, the truncate stone queue, and open connection/session/cursor handles. The code intentionally leaks some thread-owned structures after join because monitor and summary code may still read counters. Reopen uses `final_flush=true`, while `close_conn=false` intentionally skips a clean close and may lose data.

## Dependencies And Integration Points
This file depends on `wtperf_config.c` for option parsing, `wtperf_misc.c` for logging/index/backup helpers, `wtperf_throttle.c` for throttling, `wtperf_truncate.c` for truncate steering, WiredTiger test utilities, extension build macros, and system threading/sleep/file APIs. It integrates with WiredTiger backup, tiered storage, compression extensions, statistics logging, table/index creation, and random cursor support.

## Risks
Important risks are concurrency around volatile flags and unsynchronized counters, division by zero in final summary if `total_ops` or `testsec` is zero, mixed workload percentage rounding that can eliminate low-ratio operations, complex transaction rollback paths when side tables are enabled, and fragile assumptions around truncate being single-table/single-thread. `wtperf_rand` must avoid invalid ranges when populate is disabled or when insert threads are still catching up.

## Test Signals
Useful signals include successful compile under strict C warnings, smoke runs with populate-only, read-only reopen, mixed insert/read/update, `modify` with `ops_per_txn`, `random_range`, scan tables, backup, tiered flush, and truncate workloads. Runtime artifacts to inspect are `CONFIG.wtperf`, `*.stat`, `monitor`, `monitor.json`, final operation summaries, latency histograms, and failures from `lprintf`.
