# sources/storage-engines/wiredtiger/test/model/src/core/kv_database.cpp

Purpose: implements the in-memory model database that owns tables, active transactions, checkpoints, and oldest/stable timestamps.

Important APIs and functions: `kv_database_config::from_string` parses `disaggregated` and `leader`. `create_table` enforces unique names and creates `kv_table`. `create_checkpoint` captures transaction snapshot, oldest timestamp, and stable timestamp, with nameless checkpoint overwrite semantics. `begin_transaction` allocates increasing model txn IDs and snapshots active transactions. `txn_snapshot_nolock` excludes active in-progress transactions and, for checkpoints, prepared transactions. `restart`, `start_nolock`, and `rollback_to_stable_nolock` simulate WiredTiger recovery and rollback-to-stable.

Control flow and state: recursive mutexes protect tables and transactions; separate mutexes protect checkpoints and timestamps. `clear_nolock` resets timestamps, rolls back active transactions, and clears tables. Clean restart first rolls back active transactions and creates a checkpoint; crash restart does not.

Dependencies and integration: uses `kv_table`, `kv_transaction`, `kv_checkpoint`, snapshots, `config_map`, and WiredTiger checkpoint naming constants. It is driven by workload runners and debug-log parser.

Risks and test signals: lock ordering is documented and important. Snapshot rules approximate WiredTiger behavior; prepared checkpoint handling and disaggregated precise-checkpoint simulation are high-risk areas. Test signals come from matching model return codes/state against WiredTiger and from verification after restart/RTS.
