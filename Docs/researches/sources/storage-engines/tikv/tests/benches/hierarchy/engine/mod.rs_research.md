# sources/storage-engines/tikv/tests/benches/hierarchy/engine/mod.rs

## Purpose
This module benchmarks the low-level storage engine trait operations used by TiKV's hierarchy benchmarks.

## Important APIs, Types, and Functions
`bench_engine_put` measures `Engine::put` over generated key/value pairs. `bench_engine_snapshot` measures snapshot creation. `bench_engine_get` measures `Snapshot::get` excluding snapshot creation by creating a snapshot in setup. `bench_engine` registers all three for every `BenchConfig`.

## Control Flow
Criterion `iter_batched` creates deterministic generated data with `KvGenerator`, then runs the measured operation loop. Config display includes engine, key length, and value length.

## State and Persistence Behavior
Each benchmark builds a fresh engine from the configured factory. RocksDB factories create temporary test engines; BTree engines are in-memory.

## Dependencies and Integration Points
It depends on `tikv::storage::kv::{Engine, Snapshot}`, `txn_types::Key`, `test_util::KvGenerator`, and hierarchy `BenchConfig`/`EngineFactory`.

## Risks and Test Signals
Bench results compare BTree and Rocks engine behavior at trait level. Snapshot setup placement is intentional; moving it into the measured loop would change semantics.
