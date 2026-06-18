<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_heavy.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_heavy.py

Purpose: read-heavy variant of the disaggregated cache benchmark. It stresses timestamped reads close to stable timestamp while maintaining a small amount of timestamped insert/update churn and frequent checkpoints.

Important APIs and functions: uses `Context.wiredtiger_open`, `Connection.set_timestamp`, `Session.create`, `Table`, `Operation`, `txn`, `Thread`, `Workload`, and `latency.workload_latency`. No local helpers are defined.

Control flow: open a palite-backed disaggregated leader with 8 GB cache and precise checkpointing; create a layered/disagg table; populate 500,000 rows with 8 insertion threads; create 5 update threads and 5 insert threads, each using snapshot transactions with commit timestamps; create readers at ten timestamp lags, each multiplied by 9 threads; checkpoint every 10 seconds for 90 cycles; run for 900 seconds with report interval 10 and timestamp advancement every second.

State and persistence: uses WT home data files and disaggregated page-log artifacts, with stable timestamp initialized to 1 and oldest/stable timestamps advanced by Workgen. Outputs `latency.out`.

Dependencies and integration: requires the palite shared library under `WT_BUILDDIR`, the Workgen extension, and WiredTiger disaggregated storage features. Intended as part of a family of disagg cache workloads for comparative runs.

Risks: no assertion is made on final workload return. Missing `WT_BUILDDIR` or incompatible build breaks open. Running many timestamped readers can expose old-history retention costs and disk pressure. Checkpoint comments and run-time comments should be checked if changing durations.

Test signals: populate assert, printed workload return, periodic report/stats, timestamp behavior, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_heavy.py -->
