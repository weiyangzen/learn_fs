<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/prepare_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/prepare_stress.py

Purpose: prepared-transaction stress workload derived from `evict-btree-hs.py`, aimed at cache/eviction behavior around prepared updates, timestamped reads, and long-running snapshot transactions.

Important APIs and functions: uses `txn`, `op_multi_table`, `op_log_like`, `sleep`, Workgen transaction flags `use_prepare_timestamp`, `use_commit_timestamp`, `read_timestamp_lag`, workload timestamp lag/advance options, and latency output.

Control flow: open 1 GB cache connection with logging and eviction threads; create one large-value table with table logging disabled; populate 500,000 rows in snapshot transactions; create a logging table; define read timestamp Pareto operations, prepared insert operations, commit-timestamp update operations, long-running search/update snapshot operations, and log flushes; run 50 readers, 50 prepared inserters, 10 updaters, 100 long-running threads, and logging for 400 seconds.

State and persistence: creates data and log tables, uses prepared and commit timestamps, advances oldest/stable timestamps every second, pins history with lagged reads/long transactions, and writes `latency.out`.

Dependencies and integration: stress variant of history-store eviction script for prepared transactions.

Risks: high thread count and timestamped prepared operations can be resource-intensive. Comments call update operations "Insert operations" in one place. Log-like operations double write-like activity.

Test signals: populate/workload assertions, elapsed time print, statistics log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/prepare_stress.py -->
