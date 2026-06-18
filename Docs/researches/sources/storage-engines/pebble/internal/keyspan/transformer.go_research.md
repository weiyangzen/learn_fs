# sources/storage-engines/pebble/internal/keyspan/transformer.go

## Purpose
Defines generic span transformations and an iterator adapter that applies a transformation to every returned span.

## Important APIs, Types, And Functions
`Transformer` exposes `Transform(suffixCmp, in, out)`. `TransformerFunc` adapts functions. `NoopTransform` copies bounds and keys. `VisibleTransform(snapshot)` filters keys using `base.Visible`. `TransformerIter` embeds `FragmentIterator` and overrides positioning methods to call `applyTransform`.

## Control Flow
Each `TransformerIter` positioning method delegates to the embedded iterator, propagates errors, and transforms non-nil spans into reusable `t.span`. `VisibleTransform` loops over span keys and appends only keys visible at the snapshot, treating batch visibility according to `base.Visible` with `SeqNumMax` batch snapshot.

## State And Persistence Behavior
The adapter reuses a destination span and key buffer; returned spans are overwritten on the next positioning call. It has no persistence and closes the embedded iterator.

## Dependencies And Integration Points
Depends on `base.CompareRangeSuffixes`, `base.SeqNum`, and `FragmentIterator`. `MergingIter` uses transformers to filter snapshot-visible range keys before surfacing merged spans.

## Risks And Edge Cases
Transforms must preserve bounds and any key ordering expected by callers. `NoopTransform` shallow-copies keys, so suffix/value slices remain child-owned. Empty transformed spans may be returned unless callers skip them.

## Test Signals
There is no direct transformer test in this subset, but `MergingIter` tests exercise `VisibleTransform` with snapshots.
