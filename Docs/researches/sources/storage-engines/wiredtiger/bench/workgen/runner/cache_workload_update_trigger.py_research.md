<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_update_trigger.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_update_trigger.py

Purpose: executable Workgen workload derived from `read_write_heavy.wtperf` to drive cache-update pressure. It creates 10 file-backed tables plus a logging table, populates 1,000,000 rows, then runs an 85 percent read / 15 percent update mix intended to hit the WiredTiger cache update trigger.

Important APIs and functions: imports `Context`, `latency`, `get_cache_eviction_stats`, and helpers from `runner`, plus `wiredtiger` and `workgen`. It uses `Context.wiredtiger_open`, `Session.create`, `Table`, `Operation`, `Thread`, `Workload`, `op_multi_table`, `op_log_like`, `txn`, `Key.KEYGEN_PARETO`, and `ParetoOptions`. There are no local functions or classes.

Control flow: initialize a 10 GB cache connection with logging, statistics logging, session cap, eviction threads, and I/O capacity; create and populate 10 tables; create `table:log`; construct throttled log-update and log-read threads; construct a checkpoint thread; construct bursty transaction-wrapped update and search threads that do 10,000 operations then sleep; compute thread counts from `read_ops=85` and `total_thread_num=128`; run the workload for 200 seconds.

State and persistence: writes data to WiredTiger home, persists normal and log-like tables, advances commit timestamps through Workgen transaction options, and emits `cache_eviction.stat` and `latency.stat` under `context.args.home`. Checkpoints are scheduled every 30 seconds for 10 iterations.

Dependencies and integration: relies on the Workgen Python extension, WiredTiger Python bindings, and the `runner` package. The script is meant for benchmark/perf automation rather than import use.

Risks: a likely typo sets `thread_upd10k_sleep10.options.name = "Search"` instead of naming `thread_read10k_sleep10`; comments mention `eviction_updates_trigger=30` but the connection config does not set it. The workload is resource-heavy and assumes enough disk, cache, and sessions. `op_log_like` doubles write-like operations, so throttle values are approximate.

Test signals: successful `assert ret == 0`, periodic stats log JSON, `cache_eviction.stat` trigger counters, and latency buckets in `latency.stat`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_update_trigger.py -->
