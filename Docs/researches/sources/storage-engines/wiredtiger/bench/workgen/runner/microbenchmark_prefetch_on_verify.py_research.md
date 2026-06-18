<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_on_verify.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_on_verify.py

Purpose: measures verify workload behavior when prefetch is explicitly enabled.

Important APIs and functions: uses `microbenchmark_prefetch` from the base module and constructs `Operation.OP_VERIFY` with `prefetch=(enabled=true)`.

Control flow: create and populate the benchmark database, close/reopen the connection to flush cache, run a 300-second verify workload with prefetch enabled, print prefetch stats, and close session/connection.

State and persistence: persistent populated table is reused after reopen. Statistics cursor samples connection counters after verify and writes `prefetch_stats.out`.

Dependencies and integration: intended to be compared with the off variant; expected outcome is more blocks read or different throughput when prefetch is on.

Risks: comments say reopen turns prefetch on, but prefetch is actually selected in the verify operation config while the connection default remains false. Runtime and data volume are high.

Test signals: workload assertion and prefetch stats, especially `blocks_read` relative to the off run.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_on_verify.py -->
