# sources/storage-engines/tikv/components/test_coprocessor/src/fixture.rs

## Purpose
This file builds ready-to-use coprocessor test fixtures: a canonical product table, in-memory/test-engine data insertion, committed MVCC state, read pools, quota limiters, and `Endpoint` instances.

## Important APIs, Types, And Functions
`ProductTable` wraps a `Table` with `id` as primary key and `name`/`count` sharing an index. `init_data_with_engine_and_commit` and variants initialize data into a provided engine, optionally commit it, and return `(Store<E>, Endpoint<E>, Arc<QuotaLimiter>)`. `init_data_with_details_pd_client` allows a test PD client to supply TSO values. V2 checksum variants use row codec v2 and optional checksum injection. Convenience helpers `init_data_with_commit`, `init_with_data`, `init_with_data_ext`, and `init_data_with_commit_v2_checksum` allocate a Rocks test engine internally.

## Control Flow And State
Initialization builds `StorageApiV1` from an engine and mock lock manager, wraps it in the crate's `Store`, begins a transaction, inserts all supplied rows, optionally commits, then constructs a coprocessor read pool and endpoint. Row insertion paths choose either legacy row encoding or v2 row encoding with checksum based on codec version.

## Persistence And Integration Points
The inserted state is persisted in the supplied test engine as MVCC prewrites/commits. The module integrates with `TestStorageBuilderApiV1`, `MockLockManager`, `ConcurrencyManager`, `ResourceTagFactory`, `QuotaLimiter`, `ReadPool`, and TiKV server/coprocessor configs.

## Risks And Test Signals
The product-table V2 path calls `name.unwrap()`, so V2 checksum helpers require non-null names except where callers intentionally use separate null-row helpers. Global thread-group properties are set for tests and may affect process-wide test state. The returned quota limiter is useful for tests that assert resource-limiting behavior around the endpoint.
