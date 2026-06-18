<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_storms.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_storms.py

Purpose: creates alternating bursts of read and write activity over many tables to study latency/throughput storms.

Important APIs and functions: uses `op_multi_table`, `op_log_like`, `Operation.OP_SLEEP`, `OP_CHECKPOINT`, `OP_LOG_FLUSH`, `Thread`, `Workload`, and latency output.

Control flow: open 2 GB cache connection with logging, stats, and I/O capacity; create 100 snappy-compressed tables; populate 4,000,000 rows across tables; create a log table; build throttled update/read background threads, checkpoint/log-flush threads, and four burst threads that perform 10,000 or 80,000 operations followed by sleeps; run 80 background writers, 80 background readers, 40 burst threads, checkpoint, and logging for 900 seconds.

State and persistence: stores 100 data tables and log table; connection logging/statistics are enabled; latency output is written.

Dependencies and integration: derived from wtperf read/write-heavy config and adapted to Workgen helper functions.

Risks: actual operation volume is inflated by `op_log_like`; high table count and large values need significant disk/cache. Burst synchronization is initially high but expected to drift.

Test signals: populate/workload assertions, `latency.out`, statistics log, and visible storm patterns in sample output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_storms.py -->
