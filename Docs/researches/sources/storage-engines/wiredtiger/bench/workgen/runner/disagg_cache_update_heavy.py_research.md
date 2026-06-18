<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_update_heavy.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_update_heavy.py

Purpose: update-heavy disaggregated cache workload. It emphasizes update chains and history/cache pressure on layered disaggregated storage, with small insert/read side traffic and frequent checkpoints.

Important APIs and functions: top-level Workgen use of `Context`, `Operation.OP_UPDATE`, `Operation.OP_INSERT`, `Operation.OP_SEARCH`, `txn`, `Thread`, `Workload`, timestamp lag options, `Connection.set_timestamp`, and latency output.

Control flow: open a palite-backed disaggregated leader; create one layered/disagg table with 4 KB internal/leaf pages; populate 500,000 rows; wrap update and insert operations in snapshot transactions with commit timestamps; build read timestamp operations for lags 60-195 seconds; schedule checkpoints every 10 seconds; run 90 update thread copies, 5 insert thread copies, 10 reader threads, and checkpoint thread for 900 seconds.

State and persistence: creates persistent disaggregated table state and page-log state, maintains history for timestamped reads, advances oldest/stable timestamps, and writes `latency.out`.

Dependencies and integration: requires a WiredTiger build with disaggregated storage and the palite extension. It integrates with the disagg benchmark family through identical connection/table setup and varied thread mix.

Risks: missing `WT_BUILDDIR` breaks extension loading. The run result is not asserted. Heavy updates can grow history store/page-log state and disk usage. Comments again mention 600 seconds for checkpoint count despite 900-second run.

Test signals: populate assertion, printed workload return, checkpoint and statistics logs, timestamp advancement, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_update_heavy.py -->
