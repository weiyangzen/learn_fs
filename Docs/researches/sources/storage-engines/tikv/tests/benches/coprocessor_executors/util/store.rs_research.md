# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/store.rs

## Purpose
This module names and describes store implementations used by coprocessor executor benchmarks.

## Important APIs, Types, and Functions
`MemStore` aliases `FixtureStore`; `RocksStore` aliases `SnapshotStore<Arc<RocksSnapshot>>`. `StoreDescriber` provides a static display name. Specialization gives `Memory` for `MemStore` and `RocksDB` for `RocksStore`.

## Control Flow
Bench input display code calls `StoreDescriber::name()` to produce Criterion parameter names. Generic default implementation is intentionally unimplemented and relies on concrete specializations.

## State and Persistence Behavior
No state is held. Store aliases point at state owned by fixtures and snapshots.

## Dependencies and Integration Points
It depends on TiKV transaction store traits/types and Rocks snapshots. Scan and integrated benchers use it for names and generic type selection.

## Risks and Test Signals
The file uses Rust specialization-style default impls, so compiler feature compatibility matters. Any new store type needs an explicit `StoreDescriber` implementation before use.
