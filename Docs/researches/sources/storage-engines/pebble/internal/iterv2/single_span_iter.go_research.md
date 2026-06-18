# sources/storage-engines/pebble/internal/iterv2/single_span_iter.go

## Purpose
`single_span_iter.go` implements a low-overhead `iterv2.Iter` for one keyspan containing one `keyspan.Key`, equivalent to interleaving an empty point iterator with a one-span iterator.

## Important APIs, Types, And Functions
`SingleSpanIter` stores comparer, span start/end, up to four partition boundaries, number of regions, key-bearing region index, current region, direction, presented span/KV, one key, and optional prefix. `Init` configures the span and bounds. Helpers include `computeRegions`, `regionKeys`, `emitForward`, `emitBackward`, `exhaust`, and seek helpers. It implements all `Iter` methods.

## Control Flow
`computeRegions` partitions the bounded range into gap/span/gap regions and records which region carries the span key. Forward operations emit boundary keys at region ends; backward operations emit boundary keys at region starts. `SeekGE` and `SeekLT` find the region containing the seek position. `Next`/`Prev` move between regions or handle direction switches. Prefix mode allows one nonmatching boundary before exhaustion.

## State And Persistence Behavior
State is in-memory iterator position. It returns only synthetic boundary keys and never point keys. `SetBounds` recomputes regions and exhausts current position.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `invariants`, `treesteps`, and `errors`. It is intended as an optimized building block for single-range-delete/span cases.

## Risks And Edge Cases
Handling nil unbounded boundaries, empty dynamic ranges, span entirely outside bounds, and direction switches is subtle. `NextPrefix` is illegal and always panics because the iterator never positions at point keys. `Init` invariant-checks non-nil ordered span endpoints.

## Test Signals
`single_span_iter_rand_test.go` compares random operations against `TestIter`, covering bounds and direction changes.
