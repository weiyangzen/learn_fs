# sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom_test.go

## Purpose
Tests Bloom filter serialization, hash compatibility, false-positive behavior, end-to-end policy/decoder operation, and performance.

## Important APIs, Types, And Functions
`filterStr` renders filter bytes. `newTableFilter` builds a filter through the policy. Tests include `TestSmallBloomFilter`, `TestBloomFilter`, `TestHash`, and `TestEndToEnd`. Benchmarks include `BenchmarkBloomFilterWriter`, `BenchmarkMayContain`, and `BenchmarkMayContainLarge`.

## Control Flow
Small-filter tests compare exact visual bits from RocksDB. The main Bloom test builds filters for increasing key counts, verifies size bounds and no false negatives, then samples 10K non-members and checks FPR. Hash tests compare known RocksDB values. End-to-end tests use the shared randomized harness for multiple bits/key settings.

## State And Persistence Behavior
All filter state is in-memory. The exact small-filter bytes model the persisted SSTable filter format.

## Dependencies And Integration Points
Depends on `filtertestutils`, Bloom policy internals, and RocksDB-derived expected outputs. Protects fixture compatibility and reader/writer filter behavior.

## Risks And Edge Cases
FPR checks are probabilistic and could theoretically flake, though thresholds are broad. Exact expected bytes make the test sensitive to any serialization or hash change.

## Test Signals
Signals are exact byte rendering, no false negatives, FPR under configured limits, stable hash outputs, and benchmark metrics.
