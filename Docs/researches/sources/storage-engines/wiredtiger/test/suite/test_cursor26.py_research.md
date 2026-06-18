## sources/storage-engines/wiredtiger/test/suite/test_cursor26.py

### Purpose
`test_cursor26.py` is a regression test for WT-17240. It verifies that a version cursor configured like a disaggregated drain emits both a rolled-back prepared value and the underlying committed value when the prepared update had been reconciled to disk before rollback.

### Important APIs, Types, and Functions
The class uses `conn_config` with `preserve_prepared=true`, `precise_checkpoint=true`, statistics, and a small cache. `open_version_cursor` uses `debug=(dump_version=(enabled=true,raw_key_value=true,visible_only=true,timestamp_order=true,cross_key=true,show_prepared_rollback=true))`. Helpers `commit_put`, `prepared_put_and_rollback`, `force_reconcile`, and `all_versions` wrap timestamped writes, prepared rollback, forced eviction via `debug=(release_evict_page=true)`, and version collection.

### Control Flow and State
The test creates an in-memory, non-logged integer table, commits key `1` at timestamp 10, prepares an update to value `20` at timestamp 20 with a prepared id, forces reconciliation while the prepared update is active, then rolls back at timestamp 30. It sets the stable timestamp to 30 for clean precise-checkpoint closure and collects all version cursor rows for key `1`. The expected order is rolled-back prepared row first (`start_txn == WT_TXN_ABORTED`, value 20), then surviving committed row (`start_ts == 10`, standard update type, value 10).

### Persistence and Integration
The test intentionally crosses in-memory update state with reconciliation behavior to catch a disk/image interaction. It integrates with internal version cursor options used by disaggregated drain-like consumers.

### Risks and Test Signals
The key risk is that aborted prepared history hides or drops the older committed value, preventing downstream history reconstruction. Passing confirms version cursor traversal preserves enough history after prepared rollback plus reconciliation.
