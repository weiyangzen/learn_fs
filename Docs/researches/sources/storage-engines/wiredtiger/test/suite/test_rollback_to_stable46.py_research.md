# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable46.py

Purpose: tests RTS when a table has inserts on multiple pages, eviction/reconciliation has written some stable updates to disk, and later inserts are unstable. It covers column/integer-row scenario names, in-memory/disk, and worker counts.

Important APIs/types/functions: extends RTS base; uses `SimpleDataSet`, manual cursor inserts, transaction read at timestamp 30 to trigger eviction/reconciliation, `conn.rollback_to_stable`, direct cursor searches, `session.checkpoint`, and helper `check`.

Control flow: creates 5,000-row table, pins oldest/stable to 10, inserts 5,000 records at timestamp 20, performs a read at timestamp 30 to trigger eviction/reconciliation, inserts another 2,000 records at timestamp 30, verifies values, checkpoints disk cases, runs RTS to stable 10, then verifies both timestamped insert sets are gone. It also directly searches for the unstable later records before rollback.

State and persistence behavior: because stable is 10, all timestamped inserted records should be deleted by RTS, even if some were already reconciled to disk. In-memory mode disables logging and uses connection in-memory state.

Dependencies and integration points: integrates cursor-level insertion, eviction/reconciliation side effects, checkpoint, and RTS across page boundaries.

Risks: the `format_values` entry named `column` still uses `key_format='i'`, so scenario naming may be misleading. Eviction trigger via read transaction is indirect.

Test signals: direct cursor searches confirm later inserts exist before RTS; after RTS, `check(value_a, uri, 0, 20)` and `check(value_b, uri, 0, 30)` confirm all inserted records were removed.
