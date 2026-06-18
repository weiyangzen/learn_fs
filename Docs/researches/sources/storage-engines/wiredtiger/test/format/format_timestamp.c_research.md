# sources/storage-engines/wiredtiger/test/format/format_timestamp.c

Purpose: centralizes format's timestamp lifecycle: initialize from recovery, periodically advance oldest/stable timestamps, compute safe committed bounds, and do final timestamp advancement before verification.

Important APIs and functions: `timestamp_query`, `timestamp_init`, `timestamp_minimum_committed`, `timestamp_sync_threads_commit_ts`, `timestamp_once`, `timestamp` thread, and `timestamp_teardown`. WiredTiger APIs include `WT_CONNECTION::query_timestamp` and `set_timestamp`.

Control flow: initialization queries `get=recovery` and falls back to `MIN_TIMESTAMP`. `timestamp_minimum_committed` returns one less than the minimum in-use thread commit timestamp, or delegates to predictable replay's `replay_maximum_committed`. `timestamp_once` computes oldest/stable, applies replay stop/lags rules, sets both timestamps under `g.prepare_commit_lock`, updates `g.oldest_timestamp` and `g.stable_timestamp`, and optionally traces. The timestamp thread sleeps at normal or replay-specific cadence until `g.workers_finished`.

State and persistence: owns `g.timestamp`, `g.oldest_timestamp`, `g.stable_timestamp`, and per-thread `TINFO.commit_ts` synchronization. It persists timestamp state through WiredTiger connection-level `set_timestamp`, impacting visibility, checkpoint stability, rollback-to-stable, and verification.

Dependencies and integration: used by `t.c`, `ops.c`, `replay.c`, `snap.c`, and `wts.c` precise checkpoint setup. It depends on `tinfo_list`, `g.prepare_commit_lock`, replay mode, and timestamped table configuration.

Risks and test signals: stale or unset thread commit timestamps intentionally block advancement; bad advancement can make prepared commits panic or age out snapshot verification. Signals include trace `set ts`, query failures, RTS behavior, and final verify failures caused by oldest/stable not advancing far enough.
