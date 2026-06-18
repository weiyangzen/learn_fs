<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl_bench_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/skl_bench_test.go

## Purpose
This external-package benchmark measures `SeekPrefixGE` performance on Cockroach-style MVCC keys.

## Important APIs, Types, And Functions
`BenchmarkCockroachKeysSeekPrefixGE` builds an `arenaskl.Skiplist` with `cockroachkvs.Compare`, generates random KVs, computes prefixes with `cockroachkvs.Split`, and benchmarks skip distances with and without `TrySeekUsingNext`.

## Control Flow
The benchmark fills a 64 MiB arena until full, then for skip distances 1, 2, 4, 8, and 16 repeatedly seeks to later keys, optionally enabling the next-based fast path and disabling it on wraparound.

## State And Persistence Behavior
State is benchmark-local skiplist memory; no persistence.

## Dependencies And Integration Points
It integrates `cockroachkvs`, `arenaskl`, `base.SeekGEFlags`, and Go benchmarking.

## Risks And Edge Cases
Performance is sensitive to key distribution, shared-prefix density, and whether the seek direction actually satisfies the `TrySeekUsingNext` contract.

## Test Signals
Benchmark results signal regressions in prefix seeking over realistic MVCC-key shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl_bench_test.go -->
