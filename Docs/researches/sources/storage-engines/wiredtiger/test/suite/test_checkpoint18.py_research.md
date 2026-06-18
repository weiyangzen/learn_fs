# sources/storage-engines/wiredtiger/test/suite/test_checkpoint18.py

Purpose: tests that an open checkpoint cursor pins the matching history-store checkpoint in a non-timestamped scenario while a later checkpoint advances the database and can remove the older history-store footprint.

Important APIs and types: `checkpoint_thread`, `stat.conn.checkpoint_state`, `SimpleDataSet`, `session.open_cursor(..., "checkpoint=WiredTigerCheckpoint")`, and `timing_stress_for_test=[checkpoint_slow]`.

Control flow: populate baseline data and checkpoint; start a second session with odd-key updates held open; run a background checkpoint and wait until it starts; commit the transaction during the checkpoint; update the remaining even keys; open a checkpoint cursor; take another checkpoint; then scan the first checkpoint cursor.

State and persistence behavior: the first checkpoint is potentially inconsistent with a transaction committed mid-checkpoint. The open cursor must hold the correct checkpoint and matching history-store state even after the second checkpoint writes more pages and performs cleanup.

Dependencies and integration points: integrates with checkpoint thread synchronization through connection statistics. `precise_checkpoint=true` requires a stable timestamp seed. Skipped for disaggregated and tiered hooks.

Risks: timing is sensitive because it waits on checkpoint state polling. The expected result depends on checkpoint cursor snapshot pinning rather than named checkpoint behavior.

Test signals: the final checkpoint cursor must see only `value_a` for all rows, proving neither odd-key nor even-key later writes leaked into the pinned checkpoint view.
