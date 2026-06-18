<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/many-dhandle-stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/many-dhandle-stress.py

Purpose: stresses WiredTiger dhandle/file-manager behavior with 15,000 tables, idle-close cycling, checkpoints, and access spread across many handles.

Important APIs and functions: uses `op_populate_with_range` for range-partitioned population, `op_multi_table` for multi-table access, Pareto key generation, workload option `max_idle_table_cycle`, and latency output. It also appends a hard-coded legacy path to `sys.path`.

Control flow: open a 10 GB cache connection with file manager idle close time 30, session max 1000, all/clear statistics, and JSON stats on close; create 15,000 tables; populate 15,000,000 rows using range partitioning with random range 1,500,000,000; create throttled Pareto insert threads, Pareto read threads, and a checkpoint thread; run for 900 seconds with 10 insert threads and 10 read threads.

State and persistence: creates tens of thousands of table files and statistics output. Workload tracks idle-table cycle warning threshold at 2 seconds. Writes `latency.out`.

Dependencies and integration: generated from `many-dhandle-stress.wtperf`; tests file handle and dhandle scaling. The hard-coded `sys.path` is unnecessary when run from the runner directory and may be stale.

Risks: very high file count can exceed OS limits or disk inode budgets. `max_latency=60` is much lower than comments from wtperf and may flag warnings on slower hosts. The shebang is malformed as `#/usr/bin/env python`.

Test signals: assertions, idle-table cycle warnings/fatal option, statistics log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/many-dhandle-stress.py -->
