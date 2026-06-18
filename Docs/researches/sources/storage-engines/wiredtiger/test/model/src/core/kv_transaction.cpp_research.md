# sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction.cpp

Purpose: implements model transaction lifecycle, timestamp validation, prepare/commit/rollback state transitions, and update bookkeeping.

Important APIs and functions: `add_update` stamps WiredTiger metadata onto updates and records table/key/update triples. `commit` validates failed state, prepared durable timestamp requirements, durable >= commit, stable timestamp constraints, fixes placeholder update timestamps through tables, marks committed, removes transaction back-pointers from updates, and unregisters the transaction from the database. `prepare` validates state, disallows non-timestamped/logged table updates, checks stable timestamp ordering, and marks prepared. `rollback` marks rolled back, removes all updates from tables, and unregisters. `set_commit_timestamp` validates and stores timestamps for later updates.

Control flow and state: transaction state is atomic; `_lock` protects timestamp fields and update lists. `_nontimestamped_updates` tracks updates created before a final commit timestamp was known. `_wt_id` and `_wt_base_write_gen` are preserved for debug-log imported transactions.

Dependencies and integration: owned by `kv_database`, referenced by `kv_update`, and driven by model runner/debug log parser.

Risks and test signals: destructor-safe guards can only print commit exceptions, so unexpected guard failures may be easy to miss. Prepared durable timestamp and stable timestamp rules are high-value test signals for matching WiredTiger abort/error behavior.
