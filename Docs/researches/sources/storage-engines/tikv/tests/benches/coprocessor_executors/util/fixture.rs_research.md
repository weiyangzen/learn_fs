# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/fixture.rs

## Purpose
This module creates deterministic in-memory batch fixtures and test stores for coprocessor executor benchmarks.

## Important APIs, Types, and Functions
`FixtureBuilder` stores row count, field types, and per-column `Datum` vectors. It can push sequential/random/sampled/ordered integer and float columns, decimal columns, and random fixed-length bytes columns. `build_store` inserts rows into a `test_coprocessor::Store<RocksEngine>`. `build_batch_fixture_executor` converts datum columns into raw `LazyBatchColumn`s. `BatchFixtureExecutor` implements `BatchExecutor`.

## Control Flow
Fixture builder methods append schema and data columns. Store construction inserts row-by-row inside begin/commit calls. Batch executor construction encodes datums into raw column bytes. `next_batch` splits off up to `scan_rows` values from each column, constructs `LazyBatchColumnVec`, and marks drained when the first source column is empty.

## State and Persistence Behavior
Fixture state is cloned per benchmark iteration. `BatchFixtureExecutor` mutates its columns by shifting consumed rows. No durable state is owned except optional test store contents returned by `build_store`.

## Dependencies and Integration Points
It depends on `test_coprocessor`, TiDB datatype codecs, batch executor interfaces, `async_trait`, deterministic RNG seeds, and common bencher utilities.

## Risks and Test Signals
Column count/schema alignment is enforced with assertions. Drain status depends on the first column, so empty or uneven columns would be risky. The local utility benchmark checks fixture executor overhead at higher bench levels.
