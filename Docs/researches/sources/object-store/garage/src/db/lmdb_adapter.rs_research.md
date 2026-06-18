# sources/object-store/garage/src/db/lmdb_adapter.rs

Purpose: implements `garage_db` on top of LMDB via the Heed crate.

Important APIs/types/functions: `open_db`, `LmdbDb`, `LmdbDb::init`, `IDb` implementation, `LmdbTx`, `ITx` implementation, self-referential iterator wrapper `TxAndIterator`, `tx_iter_item`, and `recommended_map_size`.

Control flow: opening creates the LMDB directory, configures max DBs/readers/map size, sets `NO_READ_AHEAD` and `NO_META_SYNC`, and adds `NO_SYNC` when fsync is disabled. It maps OutOfMemory to a detailed configuration error. `open_tree` creates named LMDB databases in a write transaction and caches handles. Transactions use one LMDB write transaction with commit/abort based on closure result.

State and persistence: LMDB environment stored under `db.lmdb`. Snapshots use compacting `copy_to_path`. Default map size is 1 TiB on 64-bit and 1 GiB on 32-bit.

Dependencies and integration points: depends on `heed`, `garage_db` traits, and `Engine::Lmdb.db_path`. Used as a default metadata engine and by DB conversion.

Risks: uses unsafe lifetime extension for read-transaction iterators; safety depends on iterator wrapper drop order. LMDB map-size and virtual-memory limits can prevent startup. `NO_SYNC` when fsync disabled trades durability for performance. Tree handles opened after transaction start are unavailable in that transaction.

Test signals: shared DB test suite runs under `feature = "lmdb"` and validates basic semantics; no adapter-specific tests for snapshot, map-size errors, or unsafe iterator edge cases.
