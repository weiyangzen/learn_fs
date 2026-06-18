# sources/storage-engines/tikv/tests/benches/hierarchy/storage/mod.rs

## Purpose
This module benchmarks TiKV's high-level synchronous test storage API for raw get, prewrite, and commit.

## Important APIs, Types, and Functions
`storage_raw_get` builds a `SyncTestStorageBuilderApiV1` store and measures `raw_get`. `storage_prewrite` measures one put mutation prewrite per generated key. `storage_commit` prewrites generated keys in setup, then measures commit calls. `bench_storage` registers all cases.

## Control Flow
Each benchmark builds a fresh engine-backed test storage. `iter_batched` generates request data and passes references to the store into measured closures. Commit setup writes locks before measured commit calls.

## State and Persistence Behavior
The storage object owns engine-backed test state. Prewrite and commit mutate that state through the storage API.

## Dependencies and Integration Points
It depends on engine traits, `SyncTestStorageBuilderApiV1`, `KvGenerator`, `txn_types::Mutation`, `engine_traits::CF_DEFAULT`, and hierarchy configs.

## Risks and Test Signals
These benchmarks include more scheduling/storage-stack overhead than MVCC helper benchmarks. They validate the test storage builder and API signatures across engine backends.
