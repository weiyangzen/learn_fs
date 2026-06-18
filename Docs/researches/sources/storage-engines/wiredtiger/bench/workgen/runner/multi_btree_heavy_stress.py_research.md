<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multi_btree_heavy_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/multi_btree_heavy_stress.py

Purpose: compact Workgen proof-of-concept matching a multi-btree read-heavy wtperf workload, scaled down for testing.

Important APIs and functions: local `op_append`, `make_op`, and `operations` helpers; uses optional log table, `Key.KEYGEN_APPEND`, `KEYGEN_UNIFORM`, `Value`, throttled/named threads, and latency output.

Control flow: open a 1 GB cache connection with snappy compression, checkpointing, and stats logging; create 8 tables plus a log table; populate 20,000 append-operation groups; build insert, update, and grouped read operations across tables; throttle inserts/updates at 250 and reads at 1000; run 1 insert, 1 update, and 2 read threads for 30 seconds.

State and persistence: creates compressed data and log-like tables, checkpoints, and writes `latency.out`.

Dependencies and integration: benchmark precursor for heavier variants such as `maintain_low_dirty_cache.py`. Requires snappy support.

Risks: helper code duplicates runner functionality and may diverge. Comments preserve much larger wtperf settings, so readers must use actual constants. TODO questions log table config.

Test signals: populate/workload assertions, printed latency path, stats log, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multi_btree_heavy_stress.py -->
