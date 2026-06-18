# sources/storage-engines/pebble/error_iter.go

## Purpose
Defines sentinel iterator implementations that expose a fixed error or empty result while satisfying Pebble internal iterator interfaces. They are useful when callers need a non-nil iterator object even though iteration cannot produce keys.

## Important APIs, Types, And Functions
`errorIter` implements `internalIterator`; all positioning methods return nil, `Error` and `Close` return the stored error, `String` returns `"error"`, and `TreeStepsNode` exposes diagnostic tree-step metadata. `errorKeyspanIter` implements `keyspan.FragmentIterator`; all seek/navigation methods return nil plus the stored error, while `Close` is a no-op.

## Control Flow
There is no complex flow. Callers construct these iterators with an error, then all reads fail deterministically by returning nil data and the stored error through the iterator's error-returning API. `SeekPrefixGE` delegates to `SeekPrefixGEStrict` for interface consistency.

## State And Persistence Behavior
The only state is the immutable `err` field. These iterators do not hold files, buffers, bounds, or context, and they do not persist anything.

## Dependencies And Integration Points
Depends on `base.InternalKV`, seek flag types, `keyspan.FragmentIterator`, `context`, and `treesteps`. `file_cache.go` uses nil-error instances as `emptyIter` and `emptyKeyspanIter`, letting `iterSet.Point`, `RangeDeletion`, and `RangeKey` return non-nil empty iterators.

## Risks And Edge Cases
`errorKeyspanIter.Close` intentionally discards the stored error because its interface has no error return. Callers must check operation errors. A nil stored error makes these iterators behave as empty iterators, so misuse can hide a missing real iterator if the caller expected data.

## Test Signals
There are no direct tests in this file. Coverage is indirect through iterator construction, file cache `iterSet` behavior, and any code path that uses empty or error iterators for absent key kinds.
