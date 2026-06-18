<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_large_hs.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_large_hs.py

Purpose: rollback-to-stable microbenchmark for a large history store. It writes stable and unstable content, then updates all rows to push versions into the history store before measuring RTS.

Important APIs and functions: local `large_updates(session, uri, value, start, end, timestamp)`, direct timestamped transactions, `Connection.rollback_to_stable`, `Operation.OP_RTS`, and `latency.workload_latency`.

Control flow: create table; write 1,000,001 stable-ish rows at timestamp 5 for the upper tenth and unstable rows at timestamp 10 for lower tenth; checkpoint; update every row to `"bbbb"` at timestamp 15 to create history; checkpoint; set stable timestamp 5; call direct `rollback_to_stable`; then run a Workgen RTS operation and write `rts_large_hs.out`.

State and persistence: intentionally creates large history-store content and unstable versions. Direct RTS before Workgen RTS changes database state before measurement, so the Workgen RTS may measure a second/no-op path.

Dependencies and integration: uses helper functions from `microbenchmark_rts_unstable_content`.

Risks: very high row count and one transaction per row are extremely expensive. Opens a cursor inside each loop iteration for the second update phase but closes only the last cursor, creating possible resource pressure. Calls `show(uri, session, context.args)` after `session.close()`, which is a likely bug.

Test signals: workload assertion and `rts_large_hs.out`; direct `rollback_to_stable` should not fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_large_hs.py -->
