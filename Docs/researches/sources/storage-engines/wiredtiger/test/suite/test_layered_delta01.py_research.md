# sources/storage-engines/wiredtiger/test/suite/test_layered_delta01.py

Purpose: baseline leaf page delta read/write coverage for layered disaggregated tables. It verifies follower reads across updates, modifies, deletes, inserts, multiple deltas, and delete/insert cycles under encryption and compression scenarios.

Important APIs and functions: `test_layered_delta01` uses `DisaggConfigMixin`, `@disagg_test_class`, compression and encryption extension loading, `page_delta=(delta_pct=100)`, `stat.conn.rec_page_delta_leaf`, timestamped transactions, `wiredtiger.Modify`, checkpointing, and reopening as a follower with `checkpoint_meta`.

Control flow: each test creates a layered table, loads initial timestamped values, checkpoints, applies a second timestamped mutation type, checkpoints again, asserts at least one leaf delta was reconciled, reopens with follower disaggregated configuration, and verifies historical reads at older and newer read timestamps.

State and persistence behavior: leader checkpoints generate base images and deltas in the disaggregated page log. Follower reopen consumes complete checkpoint metadata and must reconstruct correct historical values from base plus delta chains. Deletes are verified with `WT_NOTFOUND`; modifies verify partial-value reconstruction.

Dependencies and integration: integrates page delta reconciliation, compression/encryption extensions, timestamp visibility, follower checkpoint metadata, and layered table storage. Risks include delta corruption under compression/encryption, timestamp history loss, delete tombstones not replaying, and insert ranges not materializing. Test signals are leaf delta statistic increments and exhaustive key/value checks under both read timestamps.
