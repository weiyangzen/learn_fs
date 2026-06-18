<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_with_flush.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_with_flush.py

Purpose: tiered-storage benchmark measuring checkpoints when alternating normal checkpoints with forced `flush_tier`.

Important APIs and functions: imports `microbenchmark_tiered`, builds a checkpoint thread using `Operation.OP_SLEEP`, `Operation.OP_CHECKPOINT`, and checkpoint config `flush_tier=(enabled,force)`.

Control flow: create base tiered benchmark, populate tables, set a checkpoint operation sequence of sleep 30, checkpoint, sleep 30, forced flush-tier checkpoint, then run the standard mixed workload and assert flush-tier stats.

State and persistence: writes table data to WT home and tiered bucket, triggers object flushes, and writes latency/statistics artifacts.

Dependencies and integration: direct pair with `microbenchmark_tiered_checkpoint_without_flush.py`; comparison isolates forced flush-tier overhead.

Risks: depends on base class dir_store extension path. `print_stats` expects at least three flushes during 300-second run; slow flushes or altered timing may fail despite correct behavior.

Test signals: base assertions, `flush_tier > 2`, statistics logs, and latency file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_with_flush.py -->
