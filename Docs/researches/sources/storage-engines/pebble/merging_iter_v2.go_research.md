# sources/storage-engines/pebble/merging_iter_v2.go

## Purpose
`merging_iter_v2.go` implements `mergingIterV2`, a newer slab-based point-key merging iterator over `iterv2.Iter` children. It exposes `base.TopLevelIterator`/`base.InternalIterator` behavior while using span metadata from child iterators to filter range-deleted points and park fully shadowed lower levels.

## Important APIs, types, and functions
The main types are `mergingIterV2`, `mergingIterV2Level`, `mergingIterV2Heap`, and `spanKeysChangeDetector`. `mergingIterV2Level` tracks an `iterv2.Iter`, cached `iterKV`, stashed `Span`, visibility interval `[minSeqNum,maxSeqNum)`, parked state, forward-only parking safety, and deferred boundary state.

Core methods include `Init`, `newMergingIterV2`, `First`, `SeekGE`, `SeekPrefixGE`, `SeekPrefixGEStrict`, `SeekLT`, `Last`, `Next`, `NextPrefix`, `Prev`, `Close`, `PrepareForReuse`, `SetBounds`, and `SetContext`. Internal control paths include `seekGE`, `seekLT`, `findNextEntry`, `findPrevEntry`, `advanceSlabForward`, `advanceSlabBackward`, direction switches, single-level fast paths, and batch refresh handling.

## Control flow and state behavior
Positioning calls run `slab.Build` to compute per-level visibility and parked status. Active levels are positioned with `First`, `Last`, `SeekGE`, `SeekPrefixGE`, or `SeekLT`, and then inserted into a min or max heap. `findNextEntry` and `findPrevEntry` consume span-boundary keys internally, advance slabs, and return only point keys whose sequence numbers fall within `[minSeqNum,maxSeqNum)`.

Slab transitions handle co-located boundary keys, skip advancing levels that become parked, and seek unparked lower levels to the boundary. `onlyFwdSinceParked` permits `TrySeekUsingNext` when a parked level has only been logically advanced forward. `SeekGE(TrySeekUsingNext)` includes checks to avoid moving child iterators backward, a single-level fast path when span keys are unchanged, and special `BatchJustRefreshed` logic for indexed batches that may expose newly inserted keys behind the current position.

State is transient and reusable. `PrepareForReuse` preserves backing slices for allocation reduction, `Close` closes child iterators and clears references, and `levelHasError` clears active state when a child errors.

## Dependencies and integration points
The implementation depends on `iterv2.Iter`, `iterv2.Span`, `base.InternalKeyKindSpanBoundary`, `keyspan.Key`, `slabState` from `merging_iter_v2_slab.go`, treesteps, invariants, and Pebble comparers. Range keys are intentionally handled above this iterator, not emitted here.

## Risks and test signals
Risk concentrates around slab boundary correctness, parking/unparking, prefix seek restrictions, batch refresh reseeks, boundary-key tie ordering, and avoiding stale span-key assumptions in fast paths. Tests include datadriven scenarios, randomized comparison against a reference merge, heap benchmarks, and wider metamorphic iterator workloads.
