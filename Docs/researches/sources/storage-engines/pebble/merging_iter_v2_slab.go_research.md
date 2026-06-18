# sources/storage-engines/pebble/merging_iter_v2_slab.go

## Purpose
`merging_iter_v2_slab.go` owns slab-state computation for `mergingIterV2`. It determines which levels are active or parked, computes per-level sequence-number visibility intervals, and tracks the next unshadowed span boundary.

## Important APIs, types, and functions
`slabState` stores the comparer, read snapshot, batch snapshot, batch level index, alias to `mergingIterV2` levels, and invariant-only `nextBoundary`. `Build(dir int8)` is the primary API and returns an iterator over `(levelIdx, parked)` pairs. `calcNextBoundary`, `assertNextBoundary`, and `visibleRangeDelSeqNum` support boundary and visibility logic.

## Control flow and state behavior
`Build` walks levels from newest to oldest. It yields whether the current level should be parked, expecting the caller to position the level or leave it alone. After the caller resumes, `Build` inspects the level's current span, sets `maxSeqNum` to either `snapshot` or `batchSnapshot`, detects the highest visible range deletion, and assigns `minSeqNum` to shadow lower-level keys. Once a visible range delete is found, all lower levels are parked because LSM ordering guarantees their sequence numbers are lower.

Under invariants, the code asserts that lower-level visible range deletions have smaller sequence numbers than higher-level visible range deletions. `calcNextBoundary` records the nearest non-parked span boundary in the iteration direction, used by `mergingIterV2` to assert boundary-key handling.

State is transient and aliases `m.levels`; there is no persistence. The boundary copy exists only in invariant builds.

## Dependencies and integration points
This file depends on `iter.Seq2`, `iterv2.Span`, `keyspan.Key`, `base.SeqNum`, comparers, and `internal/invariants`. It is called by every v2 positioning operation and slab transition.

## Risks and test signals
The highest-risk logic is the callback-style `Build` contract: callers must position spans before continuing, and mistakes can compute visibility from stale spans. Batch snapshot handling, parked-level propagation, and boundary direction comparisons are also sensitive. Coverage comes indirectly through all v2 datadriven and randomized tests, with invariant builds adding boundary and LSM-order assertions.
