# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable09.py

Purpose: tests timestamped schema operations under RTS: creating a table, creating an index, rolling back to stable, then dropping the table and validating object visibility. It runs both column-style and row-style table definitions, in-memory/disk modes, prepared/non-prepared schema transactions, and worker counts.

Important APIs/types/functions: defines `create_table`, `create_index`, and `drop_table` helper methods using explicit transactions and optional prepare/commit/durable timestamps. It uses `session.create`, `session.drop`, `session.open_cursor`, `conn.rollback_to_stable`, `os.path.exists`, and `wiredtiger.WiredTigerError`.

Control flow: pins oldest/stable at 10, creates the table at timestamp 20, creates the index at 30, runs RTS, then verifies the table and index still exist and can be opened. It then drops the table at timestamp 40 and asserts that both table and index cursors fail to open.

State and persistence behavior: table and index metadata must survive RTS even though created after the initial stable timestamp, reflecting special handling for durable schema operations. Disk mode additionally checks `.wt` and `.wti` file existence.

Dependencies and integration points: uses WiredTiger metadata/schema APIs, secondary index naming, Python filesystem checks, and the RTS helper base. The test integrates with the broader metadata rollback path rather than only data-page rollback.

Risks: schema timestamp semantics differ from row updates, so incorrectly treating metadata like unstable data can remove objects. In-memory mode lacks file existence checks and relies on cursor open behavior.

Test signals: successful cursor opens after RTS, `WT_NOTFOUND` on empty cursors, file existence in disk mode, and expected `WiredTigerError` after timestamped drop.
