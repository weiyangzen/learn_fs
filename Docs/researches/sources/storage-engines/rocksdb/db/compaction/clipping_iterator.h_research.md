# sources/storage-engines/rocksdb/db/compaction/clipping_iterator.h

## Purpose

`ClippingIterator` is an `InternalIterator` wrapper that restricts another internal iterator to an optional half-open key range `[start, end)`. It is used when compaction or table iteration needs a local range view even if the underlying iterator may not enforce the same bounds.

## Important APIs and Types

- Constructor: `ClippingIterator(InternalIterator* iter, const Slice* start, const Slice* end, const CompareInterface* cmp)`.
- Standard iterator methods: `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `NextAndGetResult`, `Prev`, `key`, `user_key`, `value`, `status`, and `PrepareValue`.
- Bound-related methods: `MayBeOutOfLowerBound()` always returns false for valid clipped positions; `UpperBoundCheckResult()` always reports `kInbound` for valid clipped positions.
- Delegated methods: `SetPinnedItersMgr`, `IsKeyPinned`, `IsValuePinned`, `GetProperty`, and `IsDeleteRangeSentinelKey`.

## Control Flow

The constructor asserts non-null iterator/comparator and valid bound ordering, then initializes `valid_` by checking the current position against both bounds.

Forward operations:

- `SeekToFirst()` seeks to `start` when a lower bound exists, otherwise to the underlying first key, then enforces the upper bound.
- `Seek(target)` seeks to `start` if the target is below the lower bound, returns invalid immediately if the target is at or beyond `end`, otherwise seeks to target and enforces the upper bound.
- `Next()` and `NextAndGetResult()` advance the underlying iterator and invalidate the wrapper at `end`.

Reverse operations:

- `SeekToLast()` uses `SeekForPrev(end)` when an upper bound exists and steps back if the underlying iterator lands exactly on the exclusive end key.
- `SeekForPrev(target)` returns invalid when target is below `start`, maps targets at or past `end` to the last key strictly below `end`, otherwise delegates to `SeekForPrev(target)`.
- `Prev()` steps backward and enforces the lower bound.

The wrapper uses `UpdateValid()`, `EnforceUpperBound()`, `EnforceLowerBound()`, and `AssertBounds()` to keep `valid_` independent from the wrapped iterator's raw validity.

## State and Persistence Behavior

`ClippingIterator` owns no persistent data and does not own the wrapped iterator. It stores raw pointers to the iterator, optional `Slice` bounds, comparator, and a local `valid_` flag. Bound slices must outlive the wrapper. It has no disk, manifest, or table-state persistence behavior.

## Dependencies and Integration Points

The class depends on `rocksdb/comparator.h`, `table/internal_iterator.h`, `Slice`, `CompareInterface`, and `InternalIterator` bound-check APIs. It benefits from underlying iterators that already report `MayBeOutOfLowerBound()` and `UpperBoundCheckResult()`: when those are definitive, it avoids redundant comparisons; when they are unknown, it compares keys itself.

## Risks and Edge Cases

- The wrapper assumes bounds and comparator remain valid for its lifetime.
- `SeekToLast()` and `SeekForPrev()` must handle the exclusive upper bound carefully when a key equals `end`.
- `NextAndGetResult()` must rewrite returned `bound_check_result` to `kInbound` so callers can trust the clipped iterator's public contract.
- If the underlying iterator misreports bound checks, `ClippingIterator` can incorrectly trust inbound/out-of-bound results.
- Methods assert `valid_` before key/value/pinning operations, matching normal `InternalIterator` contracts.

## Test Signals

Coverage comes from `clipping_iterator_test.cc`, which parameterizes over plain and bounds-checking vector iterators plus many start/end windows. The test checks forward, backward, seek, seek-for-prev, `NextAndGetResult()`, lower-bound reporting, and upper-bound reporting.
