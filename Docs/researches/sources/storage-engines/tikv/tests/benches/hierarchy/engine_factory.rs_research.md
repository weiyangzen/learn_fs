# sources/storage-engines/tikv/tests/benches/hierarchy/engine_factory.rs

## Purpose
This module abstracts engine construction for hierarchy benchmarks.

## Important APIs, Types, and Functions
`EngineFactory<E>` defines `build`. `BTreeEngineFactory` builds `BTreeEngine::default()` and displays as `BTree`. `RocksEngineFactory` builds a `RocksEngine` via `TestEngineBuilder::new().build().unwrap()` and displays as `Rocks`.

## Control Flow
Benchmark configuration code passes factories into generic bench modules, allowing identical benchmark code to run against both engine implementations.

## State and Persistence Behavior
Factories are stateless, clone/copy values. Built engines own their own test state; Rocks engines may create temporary disk-backed resources through the builder.

## Dependencies and Integration Points
It depends on TiKV storage `Engine`, `TestEngineBuilder`, `BTreeEngine`, and `RocksEngine`. The hierarchy runner uses it for engine, MVCC, transaction, and storage benchmark suites.

## Risks and Test Signals
`unwrap()` on Rocks engine build fails loudly for environment or engine initialization regressions. Debug names are part of Criterion benchmark identifiers.
