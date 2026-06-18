<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_long.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_long.py

Purpose: long synchronized read/write workload that alternates phases of readers, writers, both, and idle periods against a background load.

Important APIs and functions: uses `timed(seconds, ops)` and `sleep(seconds)` runner helpers, `Thread.synchronized = True`, multi-table/log-like helpers, and latency output.

Control flow: create/populate 100 snappy tables and a log table; build throttled background update/read threads, checkpoint and log-flush threads; build synchronized writer thread active for 240 seconds then idle 240 seconds; build synchronized reader thread active in a 120/240/120-second pattern; run 20 background writers, 20 background readers, 50 synchronized writers, 50 synchronized readers, checkpoint, and logging for 1,800 seconds.

State and persistence: persistent multi-table data/log state, periodic checkpoints/log flushes, statistics and latency artifacts.

Dependencies and integration: demonstrates Workgen synchronization and timed operation helpers.

Risks: long 30-minute runtime and high thread count. Imported `sys` is unused. Thread synchronization behavior depends on Workgen scheduler semantics; modifications can easily change phase alignment.

Test signals: workload assertions, phase patterns in reports, statistics log, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_long.py -->
