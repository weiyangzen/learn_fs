# sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_dirty_trigger.py

## Purpose
This workgen runner creates a cache dirty-trigger workload with mixed table updates, reads, log-like traffic, and bursty operation storms. It is adapted from a generated wtperf workload and tuned to pressure eviction/update triggers.

## Important APIs, Types, and Functions
It uses `Context`, `Table`, `Operation`, `Thread`, `Workload`, `op_multi_table`, `op_log_like`, `txn`, `get_cache_eviction_stats`, and `latency.workload_latency`. Connection config sets cache size, eviction threads, logging, session max, fast statistics, statistics logging, and IO capacity.

## Control Flow
The script opens a WiredTiger connection, creates ten file tables, populates one million records across them, creates a logged table, defines throttled log update/read threads, defines transactional multi-table update and read storm threads with sleep cycles, computes 128 total workload threads split by read percentage, runs for 200 seconds with latency sampling, then writes cache eviction stats and latency stats under the test home.

## State, Persistence, and Dependencies
Persistent state includes the workload home, tables, log table, statistics log, `cache_eviction.stat`, and `latency.stat`. Dependencies include built workgen bindings, WiredTiger Python module, and runner helper functions.

## Integration Points, Risks, and Test Signals
It integrates cache pressure, eviction stats, latency sampling, logging, and multi-table transactional operations. Risks include high thread/resource demand, a likely typo assigning `"Search"` to `thread_upd10k_sleep10.options.name` instead of the read thread, and no CLI-level parameterization. Signals are workload return code zero and generated stat/latency files.
