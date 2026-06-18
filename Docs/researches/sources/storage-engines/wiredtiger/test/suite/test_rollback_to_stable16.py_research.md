# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable16.py

Purpose: verifies RTS removes whole key ranges that only have unstable updates while preserving earlier ranges. It covers column/integer-row formats, string values, in-memory/disk modes, and worker counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. It defines `insert_update_data` for timestamped range inserts and a local `check` that can expect either a value or missing keys. Uses `conn.rollback_to_stable`, `simulate_crash_restart` import, and stats for updates aborted plus keys removed.

Control flow: creates a table, pins timestamps at 1, writes four disjoint 200-key ranges at increasing timestamps, sets stable to 5, optionally checkpoints, runs RTS, then verifies ranges at timestamps 2 and 5 survive while ranges at 7 and 9 are absent.

State and persistence behavior: the test's core state is key-range existence, not just value replacement. RTS may account for cleanup as update aborts or key removals depending on whether content was reconciled.

Dependencies and integration points: depends on WiredTiger cursor search semantics and `WT_NOTFOUND` behavior through `wiredtiger` imports. It uses scenario-generated formats and RTS logs.

Risks: count expectations combine two counters because eviction/checkpoint state can alter whether deletions are represented as aborted updates or removed keys. In-memory mode changes persistence pressure.

Test signals: range-specific checks and `upd_aborted + keys_removed >= (nrows * 2) - 2`, proving the two unstable ranges were eliminated.
