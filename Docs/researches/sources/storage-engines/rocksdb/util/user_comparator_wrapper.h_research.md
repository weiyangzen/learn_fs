# sources/storage-engines/rocksdb/util/user_comparator_wrapper.h

## Purpose

Wraps a RocksDB user comparator while incrementing `perf_context.user_key_comparison_count` for key comparison operations.

## APIs, control flow, and state

The wrapper stores a raw `const Comparator*`. `Compare`, `Equal`, and both `CompareWithoutTimestamp` overloads increment the perf counter before delegating. `CompareTimestamp` delegates without incrementing the user-key counter, and `EqualWithoutTimestamp` delegates without incrementing. The default constructor leaves the pointer null and is explicitly unusable for comparisons.

## Dependencies and integration

It depends on `monitoring/perf_context_imp.h` and `rocksdb/comparator.h`. It integrates with internal key/comparator paths that need performance accounting while preserving comparator semantics.

## Risks and test signals

There are no direct tests here. Risks include null default instances causing segmentation if used, raw comparator lifetime, and inconsistencies in which comparator methods should count as user-key comparisons. The header comment documents the default-constructor hazard.
