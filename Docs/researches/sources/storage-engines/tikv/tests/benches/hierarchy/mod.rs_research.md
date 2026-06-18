# sources/storage-engines/tikv/tests/benches/hierarchy/mod.rs

## Purpose
This is the entry point for hierarchy benchmarks that compare costs at engine, MVCC, transaction, and storage API layers.

## Important APIs, Types, and Functions
It declares child modules, default iterations/key/value lengths, `BenchConfig<F>`, `load_configs`, and `main`. `BenchConfig` records key length, value length, and engine factory, with a compact debug representation.

## Control Flow
`main` creates Criterion from CLI args, loads BTree and Rocks configs, then runs `bench_engine`, `bench_mvcc`, `bench_txn`, and `bench_storage` for both engine families before final summary.

## State and Persistence Behavior
No persistent state is held in this module. Child benchmark modules create engines and stores per test.

## Dependencies and Integration Points
It depends on Criterion, TiKV storage `Engine`, local engine factories, and all hierarchy child benchmark modules.

## Risks and Test Signals
Default config breadth is small: one key length and two value lengths. It is useful for relative cost layering, not exhaustive performance characterization.
