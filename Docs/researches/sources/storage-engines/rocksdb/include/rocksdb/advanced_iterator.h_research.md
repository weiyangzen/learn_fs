<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_iterator.h -->
# sources/storage-engines/rocksdb/include/rocksdb/advanced_iterator.h

## Purpose

`advanced_iterator.h` declares small advanced iterator result types used by lower-level table iterators to communicate bound-check and lazy-value state to RocksDB iterator code. It supports optimized `NextAndGetResult()`-style paths without forcing immediate value materialization.

## Important APIs, Types, and Functions

- `enum class IterBoundCheck : char` has `kUnknown`, `kOutOfBound`, and `kInbound`.
- `struct IterateResult` contains `Slice key`, `IterBoundCheck bound_check_result`, and `bool value_prepared`.

## Control Flow

The header contains no executable flow. A table iterator returns an `IterateResult` after advancing. If it remains valid, it should set `bound_check_result` to `kInbound`; if it becomes invalid because the next key is outside an upper/lower bound, it can report `kOutOfBound`; otherwise EOF/unknown invalidation remains `kUnknown`. If `value_prepared` is false, higher iterator layers must call `PrepareValue()` before reading `value()`.

## State and Persistence Behavior

`IterateResult::key` is a borrowed `Slice` whose lifetime is guaranteed only until the next `Next()` or `NextAndGetResult()` call. The struct carries transient iterator state only and has no persistence behavior.

## Dependencies and Integration Points

It depends only on `rocksdb/slice.h` and is consumed by advanced/table iterator implementations that can separate key movement from value preparation. It integrates with iterator bound checking and lazy value materialization in table readers.

## Risks and Edge Cases

Misreporting `value_prepared` can cause callers to read an unmaterialized value or redundantly prepare one. Misreporting `kOutOfBound` versus `kUnknown` can affect upper-layer iterator control flow and performance. The borrowed key lifetime is short and must not be stored by callers beyond the next iterator movement.

## Test Signals

Signals include iterator tests for `NextAndGetResult()` across valid keys, EOF, bound exits, and lazy value paths where `PrepareValue()` is required exactly before `value()` access.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/advanced_iterator.h -->
