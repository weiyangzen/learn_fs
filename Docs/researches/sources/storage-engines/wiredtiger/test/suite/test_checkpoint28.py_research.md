# sources/storage-engines/wiredtiger/test/suite/test_checkpoint28.py

Purpose: verifies checkpoint visibility for a prepared transaction committed during a checkpoint where commit and durable timestamps straddle the checkpoint's stable timestamp, across two tables.

Important APIs and types: `checkpoint_thread`, `stat.conn.checkpoint_state`, prepared transaction calls, `timing_stress_for_test=[checkpoint_handle]`, and checkpoint cursors.

Control flow: create two tables, prepare full-table updates at timestamp 20, advance stable to 30, start a background checkpoint and wait for it to start, commit at timestamp 25 with durable timestamp 35, open checkpoint cursors on both tables, and scan them.

State and persistence behavior: the checkpoint should not expose the prepared transaction because its durable timestamp is after stable. The two-table setup checks consistent handling across handles in the checkpoint.

Dependencies and integration points: depends on checkpoint stress timing, prepared transaction visibility, stable/durable timestamp rules, and checkpoint cursor reads. Skipped for tiered and disaggregated hooks.

Risks: checkpoint timing is synchronization-sensitive. The test asserts both tables have identical zero-row visibility in the checkpoint for the inserted rows.

Test signals: checkpoint cursors for both tables scan zero rows, proving prepared updates did not become visible in the checkpoint.
