# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable07.py

Purpose: tests recovery-time RTS after a simulated crash where stable data exists and later updates were checkpointed. It validates that restart recovery rolls pages back to the configured stable timestamp without requiring an explicit runtime RTS call.

Important APIs/types/functions: `test_rollback_to_stable07` extends `test_rollback_to_stable_base`; uses `simulate_crash_restart`, `SimpleDataSet`, `conn.set_timestamp`, `session.checkpoint`, helper `large_updates`/`check`, and `stat.conn.txn_rts*` counters.

Control flow: creates one table, pins timestamps at 10, writes values at 20/30/40/50, moves stable to 50 for prepared or 40 for non-prepared, writes additional values at 60/70/80, checkpoints, then simulates crash/restart. After restart, reads verify that timestamps at and beyond stable resolve to the last stable value, while older timestamps still resolve to their historical values.

State and persistence behavior: the checkpoint deliberately persists updates newer than stable so recovery must rollback persisted unstable content. Prepared variants require stable timestamp 50 because the prepared update at commit 50 has a durable timestamp after its prepare timestamp. No explicit `rollback_to_stable` is invoked after restart.

Dependencies and integration points: integrates recovery helper `simulate_crash_restart` and WiredTiger recovery RTS. Statistics are read after restart, where recovery-time RTS should already have run.

Risks: crash simulation and checkpoint content are timing-sensitive. If checkpoint does not include expected unstable updates, stats may show less work. Prepared timestamp choices must remain aligned with helper behavior.

Test signals: post-restart data visibility is the main signal. Statistics assert zero explicit RTS calls, no keys removed/restored, no updates aborted, and nonnegative history-store removal, proving recovery handled the persisted state consistently.
