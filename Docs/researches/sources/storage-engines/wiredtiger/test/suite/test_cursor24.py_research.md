## sources/storage-engines/wiredtiger/test/suite/test_cursor24.py

### Purpose
`test_cursor24.py` validates version cursor metadata for prepared transactions, especially prepare timestamp fields and rollback visibility. It covers committed prepared inserts, committed prepared tombstones, rolled-back prepared inserts, later committed updates after rollback, and non-prepared update chains.

### Important APIs, Types, and Functions
The class `test_cursor24` derives from `wttest.WiredTigerTestCase` and uses `make_scenarios` for row-store integer keys and variable-length column-store record-number keys. It uses `session.open_cursor(..., "debug=(dump_version=(enabled=true...))")` to open version cursors, `prepare_transaction`, `commit_transaction` with commit and durable timestamps, `rollback_transaction`, `release_evict`, and `wiredtiger.WT_NOTFOUND`. Helper methods map the version cursor value tuple: start transaction/timestamps, stop transaction/timestamps, prepare timestamps, update type, prepare state, flags, location, and value.

### Control Flow and State
Each test creates `file:test_cursor24.wt` with scenario key/value formats. `test_prepare_commit_metadata` writes a prepared insert and checks start commit/durable timestamps plus `start_prepare_ts`. `test_prepare_commit_tombstone_metadata` writes a committed value, evicts it to disk, deletes it in a prepared transaction, and verifies stop commit/durable/prepare metadata on the older value. Rollback tests assert that a rolled-back prepare with no committed base yields `WT_NOTFOUND`, and that a subsequent committed insert becomes the only visible version. The non-prepared test verifies prepare fields remain zero or max sentinel values as appropriate.

### Persistence and Integration
The suite uses WiredTiger timestamped transactions, eviction, and the internal debug version cursor, so it directly exercises storage-engine update chain interpretation. `WT_TS_MAX` is used as the expected open-ended timestamp sentinel.

### Risks and Test Signals
Risks include incorrect prepare timestamp propagation, rollback tombstones leaking as versions, and on-disk update chains losing stop metadata. Passing signals that version cursor output is consistent for both row and variable column stores across in-memory and evicted states.
