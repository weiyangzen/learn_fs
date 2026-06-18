# sources/storage-engines/pebble/internal/rangekeystack/user_iterator.go

## Purpose
This file assembles and configures the range-key iterator stack used for Pebble user iteration. It merges range-key spans across LSM levels, applies range-key semantics and snapshot visibility, bounds iteration, defragments equivalent adjacent spans, and returns user-visible range-key state.

## Important APIs, Types, and Functions
`UserIteratorConfig` owns the iterator stack: `keyspanimpl.MergingIter`, `keyspan.BoundedIter`, `keyspan.DefragmentingIter`, reusable level iterators, snapshot and comparer state, and an `internalKeys` flag. `Buffers` exposes reusable merging, defragmenting, and sort buffers. `Init` wires together merging, bounding, and defragmentation over supplied fragment iterators. `AddLevel` appends another level to the merging iterator. `NewLevelIter` reuses a fixed array before allocating. `SetBounds` updates the bounded iterator. `Transform` implements `keyspan.Transformer`, coalescing by snapshot and either returning full internal keys or user-visible sets only. `ShouldDefragment` compares two transformed spans by suffix and value to determine whether they can be joined.

## Control Flow and State
`Init` sets configuration fields, initializes the merging iterator with `ui` as transformer, wraps it in a bounded iterator, and wraps that in a defragmenter. If `internalKeys` is true, defragmentation uses internal-key semantics and `Transform` preserves unsets/deletes sorted by trailer. Otherwise, `Transform` strips unsets and deletes after coalescing and sorts visible sets by suffix. `ShouldDefragment` assumes transformed suffix order and equal-length set lists, then compares suffixes with `CompareRangeSuffixes` and values with `bytes.Equal`. State is in-memory and designed for iterator reuse through `Buffers.PrepareForReuse`.

## Dependencies and Integration
The file depends on `base`, `invariants`, `keyspan`, `keyspanimpl`, `manifest`, and `rangekey`. It is the bridge between low-level LSM level iterators and Pebble's user-facing range-key iteration API, and shares coalescing semantics with compactions and ingestion.

## Risks and Edge Cases
Correctness depends on key ordering contracts: internal mode expects trailer-descending input; user mode expects suffix-sorted coalesced output. `Buffers` must be non-nil and suitable for reuse by one active stack at a time. The defragmenter ignores sequence numbers in user mode, which is correct for user-observable state but must not leak into internal-key use. Bounds and prefix pointers are passed through to `BoundedIter`, so caller-owned pointer lifetimes matter.

## Test Signals
`user_iterator_test.go` contains datadriven tests for merging/iteration and defragmentation, randomized equivalence tests between original and fragmented spans, and a transform benchmark. These tests exercise the stack under seek/next/prev operations and defragmentation behavior.
