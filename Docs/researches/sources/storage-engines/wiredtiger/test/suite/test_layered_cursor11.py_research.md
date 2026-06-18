# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor11.py

Purpose: verifies removing a non-existent key from a layered table returns `WT_NOTFOUND`.

Important APIs/types/functions: uses `cursor.remove`, `wiredtiger.WT_NOTFOUND`, transactions, precise checkpoint follower configuration, and disaggregated scenarios.

Control flow: creates an integer-key layered table, opens a cursor, begins a transaction, sets key 1 without inserting it, asserts `cursor.remove()` returns `WT_NOTFOUND`, rolls back, and closes the cursor.

State and persistence behavior: table remains empty and the transaction is rolled back. The test validates absence handling without creating tombstones for missing keys.

Dependencies/integration points: layered remove path, notfound return semantics, transaction rollback, and follower-role local operation support.

Risks: minimal single-operation coverage. It does not test missing-key remove after checkpointed data or with tombstones.

Test signals: pass means delete of absent key returns the expected notfound code rather than succeeding or raising an unexpected error.
