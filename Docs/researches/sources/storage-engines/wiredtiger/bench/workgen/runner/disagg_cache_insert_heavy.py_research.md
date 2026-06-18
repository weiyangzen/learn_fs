<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_insert_heavy.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_insert_heavy.py

Purpose: disaggregated-storage cache workload with an insert-heavy operation mix. It targets layered/disagg table behavior under frequent checkpoints, timestamped writes, and lagged readers.

Important APIs and functions: top-level Workgen script using `Context`, `Table`, `Operation`, `Thread`, `Workload`, `txn`, `latency.workload_latency`, and `Connection.set_timestamp`. It also reads `WT_BUILDDIR` to load the palite page-log extension.

Control flow: open a leader disaggregated connection with `precise_checkpoint=true`, 8 GB cache, palite page log, and extended `cache_stuck_timeout_ms`; set stable timestamp to 1; create `table:test` as `type=layered,block_manager=disagg`; populate 500,000 rows with 8 threads; create snapshot update and insert transaction operations using commit timestamps; create 10 reader threads with read timestamp lags from 60 to 195 seconds; checkpoint every 10 seconds; run a 15-minute workload with 90 insert threads, 5 update threads, one reader per lag, and checkpointing.

State and persistence: persists layered/disagg data and page-log state in the WT home, advances oldest/stable timestamps every second using Workgen options, and writes `latency.out`.

Dependencies and integration: requires `WT_BUILDDIR/ext/page_log/palite/libwiredtiger_palite.so` and a WiredTiger build supporting disaggregated storage. Integrates with benchmark automation through output latency and statistics.

Risks: `WT_BUILDDIR` missing produces an invalid extension path. Comments say 600 seconds for checkpoint count while `run_time` is 900 seconds. The script prints the workload return value but does not assert it after run, unlike populate. Resource cost is high.

Test signals: populate assertion, workload return print, timestamped stats, checkpoint progress, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_insert_heavy.py -->
