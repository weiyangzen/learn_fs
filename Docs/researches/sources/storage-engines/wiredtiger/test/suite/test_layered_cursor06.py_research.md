# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor06.py

Purpose: verifies `next_random=true` cursors work on layered tables with data and return notfound on empty tables.

Important APIs/types/functions: uses `session.open_cursor(..., "next_random=true")`, leader checkpointing, follower reopen with `checkpoint_meta`, `wiredtiger.WT_NOTFOUND`, and disaggregated scenarios.

Control flow: `test_layered_random_cursor` creates a layered table, inserts 1,000 rows, checkpoints, inserts another 1,000 rows without checkpointing, opens a random cursor on the leader and expects `next()` success, then reopens as follower with checkpoint metadata and expects random cursor `next()` success there too. `test_empty_table` creates an empty layered table and expects random cursor `next()` to return `WT_NOTFOUND`.

State and persistence behavior: leader random cursor sees current table with both stable and newer data; follower reopen sees checkpointed data through metadata. Empty table state should not fabricate a row.

Dependencies/integration points: random cursor support, checkpoint metadata pickup, layered cursor implementation, and disaggregated leader/follower roles.

Risks: only checks success/notfound, not randomness distribution or which key is returned. Follower sees only checkpointed rows, but the test does not assert that boundary.

Test signals: pass means random cursors are supported for non-empty layered data on leader and follower and behave correctly for empty tables.
