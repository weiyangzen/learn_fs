# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor08.py

Purpose: verifies duplicate-key insert handling for layered cursors opened with `overwrite=false` under both leader and follower roles.

Important APIs/types/functions: scenarios combine disaggregated storage and role `leader`/`follower`; uses `open_cursor(..., 'overwrite=false')`, `cursor.insert`, `assertRaisesHavingMessage`, and duplicate-key error `WT_DUPLICATE_KEY`.

Control flow: creates a layered table, inserts keys `0` through `99` in timestamped transactions through an overwrite-false cursor, then sets key `10` and a different value `20`, calls `insert`, expects duplicate-key error, and asserts `get_value()` is the existing value `10`.

State and persistence behavior: table contains committed rows. A failed duplicate insert should leave the cursor positioned with the existing on-disk/logical value, not the attempted replacement value.

Dependencies/integration points: layered insert path, overwrite-false semantics, duplicate-key error propagation, cursor value state after failed insert, role-specific behavior.

Risks: follower role permits local writes in this test configuration; it does not involve checkpoint pickup. All commits use the same timestamp.

Test signals: pass means duplicate insert returns the expected error and preserves/reloads existing value state on the cursor.
