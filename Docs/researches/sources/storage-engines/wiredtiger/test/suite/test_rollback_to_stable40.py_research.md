# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable40.py

Purpose: regression test for obsolete history-store updates after globally visible updates and eviction reset page time windows. It uses a tiny table to exercise a precise history layout.

Important APIs/types/functions: extends RTS base with snapshot isolation; uses timestamped cursor updates, `session.checkpoint`, `conn.set_timestamp`, debug eviction cursor, `simulate_crash_restart`, and RTS stats.

Control flow: inserts three keys at 20, updates first/last key at 1000, updates middle key repeatedly to create history, checkpoints, pins oldest/stable to 500, evicts the globally visible update, checkpoints to move globally visible updates to a key range, writes another update at 501, opens a read at 1000, restarts, and inspects stats.

State and persistence behavior: tests that obsolete history-store records with larger timestamps are not explicitly removed in a way that corrupts stable/global visibility. Logging is enabled and cache is small to force reconciliation.

Dependencies and integration points: integrates history-store obsolescence, eviction reset of time windows, checkpoint, recovery RTS, and snapshot reads.

Risks: comments describe subtle internal behavior; small changes in reconciliation could change which updates are in history store while preserving visible results.

Test signals: direct eviction read assertion, successful restart, zero RTS calls/key removal/restoration, nonnegative aborted updates, and positive pages visited.
