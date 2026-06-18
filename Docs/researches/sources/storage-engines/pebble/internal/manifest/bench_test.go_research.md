# sources/storage-engines/pebble/internal/manifest/bench_test.go

## Purpose
This file contains an external-package benchmark for level iterator seek performance over realistic CockroachDB-style keys. It measures manifest `LevelIterator.SeekGE` behavior on a non-trivial B-tree-backed level.

## Important APIs, Types, And Functions
`BenchmarkLevelIteratorSeekGE` allocates 10,000 `manifest.TableMetadata` entries, generates random CockroachDB keys with `cockroachkvs.RandomKVs`, builds `LevelMetadata` through `manifest.MakeLevelMetadata`, creates an iterator, and repeatedly seeks keys.

## Control Flow
The benchmark creates paired keys per table, extends each table's point key bounds, initializes physical backing metadata, builds the level, resets the timer, and loops over `b.N` calls to `iter.SeekGE` using keys modulo the generated key count.

## State, Persistence, And Side Effects
State is local benchmark state. There is no persistence. The benchmark uses current time as part of random seed/config generation, so exact data distribution changes across runs, while the measured structure size remains stable.

## Dependencies And Integration Points
The file is in package `manifest_test`, so it exercises the public manifest surface rather than internal helpers. It depends on `cockroachkvs`, Pebble `base`, `manifest`, `math/rand/v2`, and `time`. It integrates manifest level metadata with CockroachDB key formatting/comparison behavior.

## Risks And Edge Cases
Because the benchmark uses time-dependent randomness, microbenchmark variance can include data-shape variance. It focuses on `SeekGE` and does not measure reverse seeks, iterator creation, deletion, copy-on-write behavior, or L0-overlap semantics. The benchmark assumes generated key pairs are suitable as smallest/largest bounds.

## Test Signals
This is a performance signal only. It is useful for detecting regressions in level iterator seek cost under realistic key distributions, but it is not a correctness test and will not fail unless setup panics.
