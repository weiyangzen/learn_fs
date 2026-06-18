<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_short.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_short.py

Purpose: shorter synchronized read/write storm workload with periodic collective alignment across read and write groups.

Important APIs and functions: uses `timed`, `sleep`, `Thread.synchronized`, `op_multi_table`, `op_log_like`, checkpoint/log flush operations, and latency output.

Control flow: setup mirrors the long sync workload: 100 tables, 4,000,000 populate rows, log table, throttled background update/read threads. It then creates synchronized write groups on 10- and 20-second cycles and read groups on 8- and 16-second cycles. Runs background, synchronized, checkpoint, and logging threads for 900 seconds.

State and persistence: persistent tables, log table, logging/statistics, and `latency.out`.

Dependencies and integration: compact synchronization demo for Workgen scheduling and phase-driven workload behavior.

Risks: high operation count and log-like amplification. Imported `sys` is unused. Because all synchronized threads start aligned, early samples can show stronger synchronization than later samples.

Test signals: assertions, report samples showing 80-second collective cycles, stats log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_short.py -->
