# sources/storage-engines/wiredtiger/test/format/snap.c

Purpose: tracks recent operations per worker so format can repeat reads/updates under snapshot isolation and validate rollback-to-stable visibility.

Important APIs and functions: `snap_init`, `snap_teardown`, `snap_op_init`, `snap_track`, `snap_repeat_txn`, `snap_repeat_update`, `snap_repeat_single`, and `snap_repeat_stable`. Static helpers decide repeatability, perform cursor verification, clear aged-out timestamps, and compare overlapping operations/truncates.

Control flow: each thread maintains circular `SNAP_OPS` buffers, two buffers when timestamps are enabled. At transaction start `snap_op_init` records read/stable timestamp context and swaps buffers when stable advances. `snap_track` saves operation type, table id, key number, row insert key, value, truncate range, and op id. Before commit, `snap_repeat_txn` verifies repeatable operations in the unresolved transaction. After commit/rollback, `snap_repeat_update` marks operations repeatable at read or commit timestamp. Later single/stable repeat paths begin read-timestamp transactions and re-read saved keys.

State and persistence: stores copies of keys/values in per-thread memory and uses timestamps to read historical persisted state. It clears entries after stable RTS verification or when timestamps age out.

Dependencies and integration: called from `ops.c` around transaction begin, operation execution, transaction resolution, and RTS. It uses `table_cursor`, key generation, `read_op`, trace macros, page dumps, and WiredTiger internal callback hooks on `WT_SESSION_IMPL::format_private`.

Risks and test signals: circular buffer wrap disables repeat checks for that transaction. Truncates are hard to repeat and mostly excluded. Snapshot mismatch prints expected/found data, dumps pages, and asserts; excessive rollback during repeat is tolerated only for oldest-for-eviction cases with a warning.
