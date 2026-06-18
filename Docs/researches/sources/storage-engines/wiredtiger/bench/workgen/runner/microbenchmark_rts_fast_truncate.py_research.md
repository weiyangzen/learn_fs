<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_fast_truncate.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_fast_truncate.py

Purpose: rollback-to-stable microbenchmark for fast truncate. It creates stable data, evicts it, checkpoints, truncates all rows at an unstable timestamp, then measures checkpoint plus RTS latency.

Important APIs and functions: imports `timestamp_str` and `show` from `microbenchmark_rts_unstable_content`; uses direct WiredTiger sessions/cursors, `debug=(release_evict)`, `Session.truncate`, `Operation.OP_CHECKPOINT`, `Operation.OP_RTS`, and latency output.

Control flow: create 1,000,000 rows at commit timestamp 10 after setting stable timestamp 5; evict rows with a debug cursor; checkpoint; open a second session and truncate the full key range at timestamp 15; run a Workgen workload containing checkpoint then RTS; emit `rts_fast_truncate.out`.

State and persistence: table contains data, then a timestamped truncate newer than stable. RTS should roll back unstable truncate effects. Eviction forces disk/read behavior.

Dependencies and integration: depends on RTS operation support in Workgen and helper display functions from the unstable-content module.

Risks: large explicit Python loops over 1M rows can be slow. Uses `show(uri, session, context.args)` after operations with an older session; fine for verbose display but can be expensive. Output filename is relative, not under `context.args.home`.

Test signals: workload assertion, latency file, optional verbose table contents, and no eviction search errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_fast_truncate.py -->
