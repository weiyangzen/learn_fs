# sources/object-store/garage/src/db/fjall_adapter.rs

Purpose: implements the `garage_db` facade over Fjall transactional keyspaces and partitions.

Important APIs/types/functions: `open_db`, `FjallDb`, `FjallDb::init`, `IDb` implementation, `FjallTx`, `ITx` implementation, iterator remappers, bound cloning helpers, and table-name `encode_name`/`decode_name`.

Control flow: opening rejects `metadata_fsync`, configures optional block cache size, and opens a transactional keyspace. `open_tree` encodes Garage tree names to safe Fjall partition names and tracks opened partitions in an `RwLock`. Single operations use read/write transactions and commit immediately. Cross-partition transactions use one `WriteTransaction`, commit on `TxFnResult::Ok`, and rollback on abort/db error.

State and persistence: Fjall partitions under `db.fjall` store Garage trees. Snapshots create a separate keyspace under the engine-specific path and copy all partitions from a read transaction before `persist(SyncAll)`.

Dependencies and integration points: depends on `fjall`, `parking_lot`, core `garage_db` traits, and `Engine::Fjall.db_path`. Used when `fjall` feature is enabled and selected in config/conversion.

Risks: marked experimental via `engine()`. Transactional `clear` is unimplemented, so user code calling `tx.clear` on Fjall will panic. Tree IDs opened after a transaction starts are intentionally invalid inside that transaction. Name encoding rejects non-byte-sized characters. Snapshot copy loops all entries and may be expensive.

Test signals: local `test_encdec_name`; shared DB test suite runs with `feature = "fjall"` and covers simple CRUD, transaction commit/abort, and iteration/range ordering.
