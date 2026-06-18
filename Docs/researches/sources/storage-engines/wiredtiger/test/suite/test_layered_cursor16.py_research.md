# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor16.py

Purpose: verifies `reserve()` behavior on layered cursors for keys present on the leader, on the follower stable constituent, on the follower ingest constituent, in both constituents, and missing from the table.

Important APIs and functions: `test_layered_cursor16` uses `@disagg_test_class`, `WiredTigerTestCase`, `session.begin_transaction`, timestamped `commit_transaction`, `session.checkpoint`, `conn.set_timestamp`, `wiredtiger_open` for a follower, `disagg_advance_checkpoint`, and cursor `reserve`. Helpers are `write`, `checkpoint`, `open_follower`, and `do_reserve`.

Control flow: each test creates the layered URI, writes or checkpoints enough data to establish one key state, then calls `do_reserve` inside a transaction. Existing keys should return `0`; missing keys are expected to raise `WiredTigerError`.

State and persistence behavior: leader tests cover pre-checkpoint and post-checkpoint data in the leader role. Follower tests split visibility between checkpointed stable data and follower-local ingest data. Transactions are rolled back after `reserve`, so the operation's lock/reservation behavior is tested without persisting additional state.

Dependencies and integration: integrates with disaggregated leader/follower opening, stable timestamp advancement, layered cursor reserve handling, and exception mapping through the Python API. Risks include treating missing layered keys as reservable, failing to search both constituents before reserving, and role-specific differences between leader and follower. Test signals are `assertEqual(..., 0)` for successful reserve and `assertRaises(wiredtiger.WiredTigerError)` for missing-key paths.
