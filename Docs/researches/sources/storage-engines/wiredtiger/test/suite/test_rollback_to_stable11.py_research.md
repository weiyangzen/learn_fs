# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable11.py

Purpose: validates recovery-time RTS when history-store content must restore a stable update after newer values are checkpointed. It covers row/column key formats and prepared/non-prepared updates.

Important APIs/types/functions: uses `simulate_crash_restart`, `SimpleDataSet`, shared `large_updates`/`check`, `conn.set_timestamp`, `session.checkpoint`, and RTS statistics for calls, key removal/restoration, history-store restore, update abort, and pages visited.

Control flow: writes a sequence of values at increasing timestamps, sets stable to the middle of the sequence, checkpoints unstable content, simulates crash/restart, and verifies reads at and after stable see the correct stable value while earlier timestamps still see their own history.

State and persistence behavior: because later updates are on disk, recovery must use the history store or in-page history to restore a stable value. Prepared mode shifts stable and read timestamps according to commit/durable timestamp rules.

Dependencies and integration points: integrates the recovery helper and `wiredtiger.stat`; inherits RTS log verification through the base class.

Risks: if reconciliation or history-store insertion changes, the exact counter mix can change. The data checks are more stable than individual statistics and protect against visible corruption.

Test signals: post-restart visibility checks plus stats expecting no explicit runtime RTS call, no key deletion/restoration surprises, and recovery work reflected in visited/aborted/history counters.
