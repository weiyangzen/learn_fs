# sources/storage-engines/tikv/tests/benches/hierarchy/mvcc/mod.rs

## Purpose
This module benchmarks MVCC primitives directly, below the high-level storage command API but above raw engine calls.

## Important APIs, Types, and Functions
`setup_prewrite` populates locks for a generated key set and returns a snapshot plus keys. Benchmarks cover `mvcc_prewrite`, `mvcc_commit`, rollback of prewrote/conflict/non-prewrote keys, `MvccReader::load_lock`, and `MvccReader::seek_write`. `bench_mvcc` registers all cases for each config.

## Control Flow
Bench functions create engines, snapshots, `ConcurrencyManager`, `MvccTxn`, `SnapshotReader` or `MvccReader`, then call transaction helper functions such as `prewrite`, `commit`, and `cleanup`. Some cases write prewrite modifies to the engine in setup using `tikv_kv::write`.

## State and Persistence Behavior
Benchmark setup mutates fresh engine instances by writing lock/write data. Measured operations generally operate on snapshots and MVCC transaction buffers; durability belongs to setup writes.

## Dependencies and Integration Points
It depends on concurrency manager, TiKV MVCC reader/txn types, transaction helpers, `KvGenerator`, `txn_types`, and hierarchy engine factories.

## Risks and Test Signals
Start timestamp selection controls whether cleanup sees prewrote, conflict, or absent state. Snapshot reuse and setup placement affect what is measured. Compile/run signals validate direct MVCC helper APIs.
