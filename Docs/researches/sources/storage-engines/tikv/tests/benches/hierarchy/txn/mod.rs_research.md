# sources/storage-engines/tikv/tests/benches/hierarchy/txn/mod.rs

## Purpose
This module benchmarks transaction helper functions plus engine write persistence, sitting between direct MVCC helper benchmarks and high-level storage API benchmarks.

## Important APIs, Types, and Functions
`setup_prewrite` writes prewrite modifies into an engine and returns keys. Benchmarks cover prewrite, commit, rollback of prewrote locks, rollback conflict, and rollback of non-prewrote keys. `bench_txn` registers cases by config.

## Control Flow
For each measured key, the benchmark obtains a fresh snapshot, creates `MvccTxn` and `SnapshotReader`, invokes `prewrite`, `commit`, or `cleanup`, converts modifies into `WriteData`, and writes them to the engine. Commit/rollback cases use setup engines populated with lock state.

## State and Persistence Behavior
Unlike `mvcc/mod.rs`, measured closures include engine writes, so benchmarks include persistence cost to the selected engine. Engines are fresh per benchmark function but mutated through iterations.

## Dependencies and Integration Points
It depends on concurrency manager, transaction helper APIs, engine `WriteData`, `KvGenerator`, `txn_types`, and hierarchy engine factories.

## Risks and Test Signals
Engine cloning in setup must preserve intended lock state. Start timestamp differences distinguish conflict/non-conflict cases. Successful runs validate transaction helper and engine write integration.
