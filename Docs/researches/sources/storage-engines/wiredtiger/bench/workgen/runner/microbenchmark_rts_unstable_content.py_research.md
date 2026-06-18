<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_unstable_content.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_unstable_content.py

Purpose: base/simple RTS microbenchmark and helper provider for other RTS scripts. It creates unstable timestamped content and measures checkpoint plus RTS latency.

Important APIs and functions: defines `show(uri, s, args)` for verbose cursor printing and `timestamp_str(t)` for timestamp formatting. In main, uses `Context`, direct WT transactions, `Operation.OP_CHECKPOINT`, `Operation.OP_RTS`, `Workload`, and `latency.workload_latency`.

Control flow: when run as a script, open database, set stable timestamp 5, create `table:rts_unstable_content`, insert 10 rows at timestamp 10, run checkpoint then RTS as Workgen operations, write `rts_unstable_content.out`, and optionally show rows.

State and persistence: table content is newer than stable timestamp and therefore subject to rollback. It also acts as a utility module for other RTS benchmarks.

Dependencies and integration: imported by fast truncate, large history store, many files, and overflow pages modules. The helper functions are intentionally lightweight.

Risks: timestamp formatting is a trivial decimal string and may not cover hex timestamp formats if needed elsewhere. The module mixes helper definitions with executable benchmark guarded by `__main__`, which is acceptable but makes imports depend on no top-level side effects.

Test signals: workload assertion, latency file, optional verbose table output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_unstable_content.py -->
