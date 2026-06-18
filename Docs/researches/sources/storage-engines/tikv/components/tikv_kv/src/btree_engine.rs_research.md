# sources/storage-engines/tikv/components/tikv_kv/src/btree_engine.rs

## Purpose
This file implements `BTreeEngine`, an in-memory `BTreeMap`-based engine used for tests and benchmarks. It mimics enough of TiKV's engine, snapshot, and iterator interfaces to run common KV tests without RocksDB.

## Important APIs, Types, and Control Flow
`BTreeEngine` owns ordered column-family names and `Arc<RwLock<BTreeMap<Key, Value>>>` contents. `new` ensures a default CF exists, and `get_cf` resolves CF name to the shared tree. The `Engine` implementation supports `async_write` by applying `Modify` values and returning a single `WriteEvent::Finished`, rejects empty writes, and returns fake snapshots through `async_snapshot` and `async_in_memory_snapshot`. `kv_engine` and `modify_on_kv_engine` are unimplemented because this is not a full local engine wrapper.

`BTreeEngineIterator` tracks the current cloned key/value, validity flag, tree reference, and bounds derived from `IterOptions`. Seek operations translate to `BTreeMap::range` over included/excluded bounds and choose either the first or last endpoint. `Snapshot` reads clone values from the underlying shared map and creates iterators.

## State, Dependencies, and Integration
All state is in memory and protected by `RwLock`. Snapshots are explicitly not isolated: they clone the engine handles, so later writes affect snapshot reads. `write_modifies` supports put, delete, and pessimistic lock writes to `CF_LOCK`; range delete and ingest are unimplemented.

## Risks and Test Signals
This engine is unsuitable for persistence, isolation, range deletion, ingestion, or exact RocksDB behavior. Iterator methods panic if key/value are read while invalid. Tests cover base CRUD, linear scans, CF statistics, iterator bounds, forward/backward movement, and panic on missing CF.
