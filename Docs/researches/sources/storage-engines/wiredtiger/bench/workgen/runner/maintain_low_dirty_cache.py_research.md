<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/maintain_low_dirty_cache.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/maintain_low_dirty_cache.py

Purpose: machine-tuned workload intended to maintain dirty cache around WiredTiger's 5 percent eviction target on AWS perf hosts while driving mixed multi-table reads, inserts, and updates.

Important APIs and functions: local `op_append`, `make_op`, and `operations` create multi-table operation sequences with optional log table and transaction grouping. Uses Workgen throttles, thread names, `latency.workload_latency`, and connection statistics.

Control flow: open a 2 GB cache connection with checkpoint every 8 seconds, snappy compression, disabled logging, and stats logging; create 8 data tables and a log table; populate 1,000,000 append rows; build log-like insert/update operations and grouped read transactions; run 4 insert threads, 9 update threads, and 90 read threads for 1,200 seconds with 1-second reporting and 5-second samples.

State and persistence: writes 8 data tables, a log-like table, checkpoints frequently, and writes `latency.out` under the connection home.

Dependencies and integration: comparator/variant of `multi_btree_heavy_stress.py` with production perf-host tuning. Requires snappy support.

Risks: comments warn tuning is machine-dependent. Long 20-minute runtime and large populate can consume disk. Log-like table additions multiply write volume.

Test signals: populate/workload assertions, statistics log, per-thread throughput names, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/maintain_low_dirty_cache.py -->
