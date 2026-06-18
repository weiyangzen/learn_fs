# sources/storage-engines/pebble/internal/keyspan/interleaving_iter.go

## Purpose
Implements `InterleavingIter`, an internal iterator that merges point keys with keyspan boundaries and tracks the span covering each returned point or synthetic boundary.

## Important APIs, Types, And Functions
`SpanMask` supports range-key masking through `SpanChanged` and `SkipPoint`. `InterleavingIterOpts` configures masking, bounds, and optional end-boundary interleaving. `InterleavingIter.Init`, `InitSeekGE`, `InitSeekLT`, `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `NextPrefix`, `Span`, `SetBounds`, `Invalidate`, `Error`, and `Close` implement `base.InternalIterator`.

## Control Flow
The iterator keeps independent point and span positions and an `interleavePos` state (`pointKey`, `keyspanStart`, `keyspanEnd`, exhausted, or bound-sentinel states). Forward movement chooses the minimum of point key and span start/end; reverse movement chooses the maximum. Synthetic span start and optional end markers use `SeqNumMax` so they sort before/after point keys as needed. Seeks may reuse a cached span if the seek remains within it, otherwise they seek the span iterator. Prefix seeks truncate spans to the prefix successor and may force reseeks if the cached defragmented span does not cover the full prefix.

## State And Persistence Behavior
State is transient: current point KV, current span pointer, truncated span copy, marker key, prefix buffers, accumulated error, direction, and mask state. Bounds and seek-key truncations copy user-provided keys into buffers where stability is needed. No persistent storage is modified.

## Dependencies And Integration Points
Depends on `base.InternalIterator`, `FragmentIterator`, `base.Comparer`, `treesteps`, invariants, and redaction. It is used by Pebble iterator stacks to expose range keys/deletions alongside point keys and by external/level iterators that combine table point and span streams.

## Risks And Edge Cases
High-risk areas include direction switches from synthetic boundaries, span marker truncation after seeks, prefix-mode invalidation, bound enforcement around exclusive upper bounds, masking that skips point keys, error accumulation from either child iterator, and stale child span pointers. Empty spans are not surfaced as markers.

## Test Signals
`interleaving_iter_test.go` exercises point/span interleaving, bounds, prefix seeks, optional end markers, masking hooks, direction changes, and a bounded test point iterator.
