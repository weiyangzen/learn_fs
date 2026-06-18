<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/iterator.go -->
# sources/storage-engines/pebble/internal/arenaskl/iterator.go

## Purpose
This file implements the arena skiplist `base.InternalIterator`, including forward/reverse seeks, bounds, strict-prefix iteration, and a small seek-using-next optimization.

## Important APIs, Types, And Functions
`Iterator` stores the skiplist, split function, current node, bounds, cached bound nodes, prefix, and current KV. Important methods include `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `Prev`, `SetBounds`, `Close`, `decodeKey`, and `seekForBaseSplice`.

## Control Flow
Seek methods descend skiplist levels through `seekForBaseSplice`, then decode and bound-check the landing node. `TrySeekUsingNext` can walk a few `Next` calls before falling back to a full seek. Prefix mode is set by `SeekPrefixGE` and enforced by `Next`.

## State And Persistence Behavior
Iterator state is pooled through `sync.Pool`. Values are returned as in-place references to arena memory. Bounds cache arbitrary nodes outside range to avoid repeated comparisons after exhaustion.

## Dependencies And Integration Points
It integrates `base.InternalIterator`, `base.Split`, seek flags, `treesteps`, and `Skiplist` link accessors. It is used by memtables and tests with both default and MVCC-like comparers.

## Risks And Edge Cases
The iterator assumes callers honor lower-bound checks for `SeekGE`/`First` and upper-bound checks for `SeekLT`/`Last`. Prefix exhaustion must still update `kv.V` to avoid stale values when a later `TrySeekUsingNext` returns the cached KV.

## Test Signals
`skl_test.go` covers basic iteration, strict-prefix behavior, prefix-exhausted fast path, bounds, seek directions, and concurrent access.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/iterator.go -->
