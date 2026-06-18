<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_base.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_base.py

Purpose: shared base class for tiered-storage checkpoint microbenchmarks.

Important APIs and functions: class `microbenchmark_tiered` with `__init__`, `populate`, `create_bucket`, `set_checkpoint_thread`, `print_stats`, and `run_workload`. It uses `op_multi_table`, `op_group_transaction`, Workgen thread composition, `wiredtiger.stat.conn.flush_tier`, and latency output.

Control flow: constructor opens a `dir_store` tiered-storage connection with a bucket directory, log/statistics enabled, and early-loaded dir_store extension; creates four file tables; prepares read, update, and insert thread templates across all tables. `populate` inserts 50,000 rows with grouped transactions. `run_workload` runs 8 readers, 2 updaters, 2 inserters, and a caller-provided checkpoint thread for 300 seconds. `print_stats` asserts more than two `flush_tier` calls.

State and persistence: creates WT home, local bucket directory, four tiered tables, logs, statistics, and `latency.out`. `create_bucket` ensures local object-store directory exists before open.

Dependencies and integration: imported by with-flush and without-flush scripts. Requires `./ext/storage_sources/dir_store/libwiredtiger_dir_store.so` relative to run directory/build.

Risks: constructor parameter `extension` is stored but not used to vary config; config always names `dir_store`. Missing extension or wrong working directory fails open. `print_stats` is meaningful only for workloads that force flush tier.

Test signals: populate/run assertions, `flush_tier > 2` assertion for flush variant, statistics log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_base.py -->
