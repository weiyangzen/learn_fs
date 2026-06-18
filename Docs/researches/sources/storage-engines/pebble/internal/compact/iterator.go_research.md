# sources/storage-engines/pebble/internal/compact/iterator.go

## Purpose
This file implements `compact.Iter`, the forward-only iterator that transforms merged LSM input streams into compaction output keys. It collapses point versions within snapshot stripes, handles MERGE semantics, elides point/range tombstones when safe, interleaves range deletions and range keys, tracks snapshot-pinned output, and surfaces metadata for value separation.

## Important APIs, Types, And Functions
`Iter` owns the wrapped iterator, interleaving range-del/range-key iterators, tombstone/range-key compactors, buffers, snapshot stripe state, last range tombstone span, frontiers, and stats. `IterConfig` provides comparer, merge operator, snapshots, tombstone elision policy, bottommost-layer flag, and anomaly callbacks. Public methods include `NewIter`, `Frontiers`, `SnapshotPinned`, `ForceObsoleteDueToRangeDel`, `Stats`, `GetCurrentMeta`, `First`, `Next`, `Span`, `Error`, and `Close`. Core helpers include `nextInStripe`, `setNext`, `mergeNext`, `singleDeleteNext`, `skipDueToSingleDeleteElision`, `deleteSizedNext`, `saveKey`, `saveValue`, and `tombstoneCovers`.

## Control Flow
`NewIter` interleaves point keys with range deletions and range keys, initializes compactors and frontiers, and wraps iterators for invariant invalidation. `First` positions the input and calls `Next`. `Next` loops over candidates, advances frontiers, processes range spans through span compactors, skips keys visibly covered by range deletes, elides deletions in the bottom stripe when lower levels do not overlap, collapses SET/SETWITHDEL records, merges MERGE operands through the configured merger, applies SINGLEDEL rules, and validates DELSIZED tombstone sizes.

## State And Persistence Behavior
The iterator itself is transient, but its transformations determine durable SST contents. It may rewrite sequence numbers to zero for bottommost snapshot stripes, convert MERGE+SET to SET, transform MERGE+DEL to SETWITHDEL, convert inaccurate DELSIZED to DEL, and mark values as snapshot-pinned for output table properties.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `rangekey`, `invalidating`, tombstone elision/span compaction helpers, and `Frontiers`. It is consumed by `Runner` and upstream Pebble compaction code that writes output tables and stats.

## Risks And Edge Cases
Risks are severe: snapshot visibility, range-delete coverage, merge barriers, SINGLEDEL determinism, DELSIZED accounting, blob/lazy value cloning, key/value lifetime, and range span stability. Comments note a subtle range span stability violation and a TODO around snapshot-pinned semantics.

## Test Signals
`iterator_test.go` drives datadriven traces for ordinary collapse, SETWITHDEL, DELSIZED, range tombstones, range keys, snapshots, tombstone elision, bottommost sequence zeroing, blob handles, and anomaly callback output.
