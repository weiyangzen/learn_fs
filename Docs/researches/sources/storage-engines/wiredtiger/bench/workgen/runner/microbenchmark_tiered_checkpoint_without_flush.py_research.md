<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_without_flush.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_without_flush.py

Purpose: tiered-storage benchmark measuring normal checkpoint latency without explicit flush-tier calls.

Important APIs and functions: uses `microbenchmark_tiered` and a simple checkpoint thread `sleep(30) + checkpoint`.

Control flow: instantiate base benchmark, populate four tables, set the checkpoint thread, and run the base mixed workload. It does not call `print_stats` because no forced flush-tier count is expected.

State and persistence: creates tiered tables and local bucket state through the base class, emits latency/statistics artifacts, and checkpoints every 30 seconds.

Dependencies and integration: control workload for the with-flush variant.

Risks: same extension/working-directory risks as the base. Without a flush assertion, success only means workload completion, not that no tiered flush occurred due to other mechanisms.

Test signals: populate and workload assertions plus latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_without_flush.py -->
