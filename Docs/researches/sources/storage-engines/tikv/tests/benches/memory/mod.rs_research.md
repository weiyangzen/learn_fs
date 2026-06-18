# sources/storage-engines/tikv/tests/benches/memory/mod.rs

## Purpose
This Criterion benchmark measures TiKV memory quota allocation/free paths in single-threaded and contended multi-threaded scenarios.

## Important APIs, Types, and Functions
`bench_memory_quota_alloc` measures successful and failed `MemoryQuota::alloc`. `bench_memory_quota_alloc_free` compares manual `alloc/free` with RAII `OwnedAllocated`. `bench_memory_quota_multi_threads` runs 32- and 64-thread contention scenarios through `memory_quota_multi_threads`.

## Control Flow
Multi-threaded benchmarks spawn background workers that repeatedly allocate and free quota until an atomic `done` flag is set. The Criterion-measured thread performs the same operations or RAII allocation while workers create contention.

## State and Persistence Behavior
State is in-memory quota counters and worker thread state. No persistence is involved.

## Dependencies and Integration Points
It depends on Criterion macros, `tikv_util::memory::{MemoryQuota, OwnedAllocated}`, atomics, threads, and `black_box`.

## Risks and Test Signals
The fixed 20 ns work-duration estimate and 500 ms check interval are CPU-sensitive. Join handling ensures background workers stop after the group. Useful signals are alloc fail/ok cost and contention scaling.
