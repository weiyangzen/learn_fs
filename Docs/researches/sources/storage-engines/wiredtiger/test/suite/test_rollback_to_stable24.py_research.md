# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable24.py

Purpose: targets RTS correctness for reconciliation where one key has a newer unstable update and another key is updated after forced eviction. It covers column and integer-row formats and worker counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Uses manual `session.create`, explicit cursor writes and timestamped commits, debug eviction cursor `debug=(release_evict)`, `conn.set_timestamp`, `conn.rollback_to_stable`, and direct cursor indexing for assertions.

Control flow: writes keys at timestamp 10, updates key 4 at 50, evicts the page, updates key 1 at 30, sets stable to 40, runs RTS, and reads at 40. Expected results are key 1's stable update, unchanged baseline values for keys 2/3, and key 4's value as of the reconciled state.

State and persistence behavior: forced eviction creates on-disk page state before the later update and RTS. The test checks that RTS handles per-key time windows correctly after reconciliation.

Dependencies and integration points: integrates low-level debug eviction with timestamped cursor operations, independent of the common base helpers.

Risks: direct key assumptions are small and precise; if column-store key allocation or eviction behavior changes, the scenario may need adjustment.

Test signals: exact cursor values for keys 1-4 at read timestamp 40 after RTS.
