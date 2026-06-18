# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable12.py

Purpose: covers recovery RTS when stable content is a remove/tombstone and newer updates must be discarded. It runs row/column formats and prepared/non-prepared updates.

Important APIs/types/functions: class extends `test_rollback_to_stable_base` and uses `large_updates`, `large_removes`, `check`, `simulate_crash_restart`, `session.checkpoint`, `conn.set_timestamp`, and `stat.conn` counters.

Control flow: creates a table, writes an initial value, removes all rows at a timestamp that becomes stable, writes newer values, checkpoints, simulates crash/restart, and verifies that reads at and after stable observe an empty table while older reads still see the original value.

State and persistence behavior: the stable state is a globally meaningful tombstone. Recovery RTS must preserve that tombstone and remove newer updates, including any history-store entries produced by the checkpoint.

Dependencies and integration points: relies on the common helper for prepared remove transactions and on recovery RTS for cleanup. It integrates with history-store and tombstone accounting.

Risks: stable deletes are easy to mishandle because restoring an older value would be incorrect once the remove is stable. Prepared timestamp offsets must match the helper's prepare/commit/durable timestamps.

Test signals: post-restart empty-table checks at stable/newer timestamps, original-value checks at older timestamps, and statistics that show recovery RTS did work without an explicit runtime RTS call.
