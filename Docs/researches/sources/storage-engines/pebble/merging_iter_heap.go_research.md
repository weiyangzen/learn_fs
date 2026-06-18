# sources/storage-engines/pebble/merging_iter_heap.go

## Purpose
`merging_iter_heap.go` provides the specialized heap used by the legacy merging iterator. It orders `mergingIterLevel` entries by their cached internal keys, supporting both forward min-heap and reverse max-heap behavior.

## Important APIs, types, and functions
`mergingIterHeap` stores the comparer, `reverse` mode, and `items []mergingIterHeapItem`. Each item holds a `*mergingIterLevel` and a cached `winnerChild`. `winnerChild` records which child would win during heap descent, reducing repeated comparisons during `down`.

The public-to-package methods are `len`, `clear`, `init`, `fixTop`, and `pop`. Internal helpers are `less`, `swap`, and `down`.

## Control flow and state behavior
`less` compares user keys first, then trailers. In forward mode, lower user keys and higher trailers win. In reverse mode, higher user keys and lower trailers win, matching reverse internal ordering. `init` heapifies in place from the bottom up. `fixTop` repairs the heap after the root's key changes. `pop` swaps the root with the final item, repairs the reduced heap, and shrinks the slice.

The only persistent state is the heap slice and cached winner-child hints. The heap assumes every item has a non-nil `iterKV`; exhaustion is handled by callers before removal. Cached `winnerChild` values are invalidated when swaps alter parent-child relationships. In invariant builds, the cache is checked for consistency.

## Dependencies and integration points
This heap is tightly coupled to `mergingIterLevel.iterKV` from `merging_iter.go` and uses Pebble's `Compare` plus invariant assertions from `internal/invariants`. It is not Go's standard `container/heap`; it is a hand-rolled implementation tuned for the small fixed fan-in of LSM levels.

## Risks and test signals
The main risks are stale `winnerChild` hints, reverse ordering mistakes, duplicate-key tie handling, and callers passing exhausted levels. `merging_iter_heap_test.go` randomly mutates heap roots, pops entries, and validates that the top always matches an independent scan. It also has a comparison-saving init test that exercises heap construction repeatedly.
