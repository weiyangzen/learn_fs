# sources/storage-engines/pebble/bench/db.go

## Purpose
`db.go` provides a narrow database abstraction for benchmarks and a Pebble-backed implementation. It centralizes benchmark-specific Pebble options so workloads can focus on access patterns.

## Important APIs, Types, And Functions
Interfaces `DB`, `Iterator`, and `Batch` capture only benchmark needs. `pebbleDB` wraps `*pebble.DB` and optional ballast. `NewPebbleDB` opens a configured Pebble instance. Methods implement `Flush`, `NewIter`, `NewBatch`, `Scan`, `Metrics`, and `Close`.

## Control Flow
`NewPebbleDB` builds `pebble.Options` with Cockroach key schema/comparer, cache, WAL, L0, memtable, compaction, blob/value separation, block-size, and shared-storage settings, then opens the DB. Verbose mode installs a logging event listener with noisy events disabled. `Scan` seeks forward or reverse and copies keys/values into a `bytealloc.A` to simulate consumption while avoiding compiler elision.

## State And Persistence Behavior
It creates or opens an on-disk Pebble DB at the requested directory and may configure remote/shared object creation. The ballast is retained in memory, not persisted. `Scan` is read-only; workloads mutate through `Batch` and `Flush`.

## Dependencies And Integration Points
The file depends on Pebble core packages, Cockroach key encoding, sstable key schemas, `remote` object storage, `vfs`, and `bytealloc`. Every DB-backed benchmark reaches Pebble through this adapter.

## Risks And Edge Cases
`NewPebbleDB` uses `log.Fatal` on open/configuration failures, which is appropriate for CLI benchmarks but not library use. `NewIter` ignores iterator creation errors. Shared-storage creator ID is hard-coded to 1 for benchmark convenience. Value separation defaults may affect comparability with older benchmark runs.

## Test Signals
No direct tests. Behavior is exercised by all benchmark workloads and `ycsb_bench_test.go` fixture generation.
