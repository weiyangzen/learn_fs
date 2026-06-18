<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_write.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_write.py

Purpose: balanced read/write disaggregated cache benchmark. It mixes timestamped inserts, updates, lagged reads, and checkpoints against one layered/disagg table to study cache behavior under roughly equal read/write pressure.

Important APIs and functions: uses the same Workgen and runner APIs as the other disagg cache scripts: `Context`, `Table`, `Operation`, `txn`, `Thread`, `Workload`, timestamp lag options, and `latency.workload_latency`.

Control flow: open a palite disaggregated leader connection; initialize stable timestamp; create a small-page layered table; populate 500,000 rows; build commit-timestamp snapshot update and insert operations; build 10 reader operation templates with read timestamp lags; assemble 50 update threads, 50 insert threads, and 5 copies of each lagged reader template; add a 10-second checkpoint loop; run for 900 seconds.

State and persistence: persistent state includes layered table pages, disaggregated page-log data, checkpoint metadata, and history needed for lagged reads. Writes `latency.out` in the configured home.

Dependencies and integration: depends on `WT_BUILDDIR` for `libwiredtiger_palite.so`. It is structurally aligned with insert/read/update-heavy variants, making it suitable for comparative performance dashboards.

Risks: comment says populate 1M rows but `icount` is 500,000. The run return is printed rather than asserted. `threads = 50 * tupdate + 50 * tinsert` yields 100,000 writes before reader multiplication, so comments about exact percentages should be verified against Workgen repetition semantics.

Test signals: populate assertion, workload return print, WiredTiger stats log, checkpoint cadence, timestamp advancement, and latency buckets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_write.py -->
