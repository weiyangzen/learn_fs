# sources/storage-engines/pebble/merging_iter_v2_bench_test.go

## Purpose
This benchmark file measures the custom heap inside `mergingIterV2`. It isolates heap initialization and repeated root repair under short and long CockroachDB-style MVCC keys.

## Important APIs, types, and functions
The only benchmark is `BenchmarkMergingIterV2Heap`. It defines short and long `cockroachkvs.KeyGenConfig` cases, then sub-benchmarks `Init` and `FixTop` for each. It directly manipulates `mergingIterV2Level`, `mergingIterV2Heap`, and `base.InternalKV`.

## Control flow and state behavior
The `Init` benchmark repeatedly fills a heap with eight level entries drawn from a shuffled random key pool, then calls `heap.Init`. The `FixTop` benchmark builds level key streams with exponential bias toward lower levels, initializes the heap, and repeatedly advances the top level or pops it when exhausted. This simulates the steady-state merge path where `Next` advances one child and repairs the heap.

No persistent state is created. State under measurement is the heap slice, per-level `iterKV` pointers, and level positions in generated arrays. The benchmark intentionally varies key length to capture compare cost sensitivity.

## Dependencies and integration points
It uses the `cockroachkvs` comparer and random key generator because CockroachDB MVCC keys are a primary Pebble workload. The benchmark is directly tied to `mergingIterV2Heap` internals and does not instantiate a full iterator or slab state.

## Risks and test signals
The benchmark is a performance signal, not a correctness oracle. It may miss correctness problems in boundary-key tie-breaking, parking, or span transitions. It is useful for detecting regressions in heap operations, especially comparison-heavy workloads with long keys.
