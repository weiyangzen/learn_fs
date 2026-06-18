# sources/storage-engines/badger/skl/skl.go

## Purpose
This file implements Badger's arena-backed concurrent skiplist, used as the ordered in-memory index for memtables. It is adapted from RocksDB's inline skiplist but simplified around Badger's key comparator, arena allocator, overwrite semantics, and lock-free/CAS pointer updates.

## Important APIs, Types, and Functions
- `Skiplist` owns the head node, arena, current height, reference count, and optional `OnClose` callback.
- `node` stores a key offset/size, atomically encoded value offset/size, height, and per-level next offsets.
- `NewSkiplist`, `IncrRef`, and `DecrRef` manage lifecycle; `DecrRef` clears arena/head when the final reference leaves.
- `Put`, `Get`, `Empty`, `MemSize`, and iterator constructors form the public surface used by Badger memtables.
- `findNear` and `findSpliceForLevel` are the core search primitives.
- `Iterator` supports bidirectional movement; `UniIterator` adapts it to Badger's `y.Iterator` style with optional reverse traversal.

## Control Flow and State Behavior
Nodes are allocated in an `Arena`, and node fields store offsets rather than heap pointers for compactness and stable memory layout. `Put` first searches from the current height downward. If the key is already present, it atomically stores a new value reference without creating a node. Otherwise it creates a random-height node, possibly raises list height via CAS, then links the node from level 0 upward with compare-and-swap on tower offsets. If a CAS conflict exposes that another goroutine inserted the same key at level 0, the existing node is overwritten.

`Get` seeks to the first key greater-or-equal to the timestamped key and then verifies `y.SameKey`, returning a decoded `ValueStruct` whose `Version` is parsed from the stored key. Iterators hold a skiplist reference and must be closed to release the arena. Reverse movement uses `findNear` with `less=true`.

## Dependencies and Integration Points
The file depends on `github.com/dgraph-io/badger/v4/y` for key comparison, timestamp parsing, assertions, and `ValueStruct`, plus `ristretto/v2/z.FastRand` for randomized height. It integrates with Badger memtables through the unidirectional iterator and through arena memory accounting.

## Risks and Edge Cases
Correctness depends on keys fitting `uint16` key sizes while values can be larger because values are stored through arena value offsets/sizes. The code is intentionally concurrent but lock-free insertion is subtle: base-level insertion must happen before higher levels, and overwrite races must only resolve at level 0. Reference counting is a lifecycle contract; failing to close iterators keeps arena memory live, while accessing after final `DecrRef` is invalid. Value replacement appends a new value in the arena, so repeated overwrites grow memory until the memtable is flushed.

## Test Signals
`skl_test.go` covers empty-list behavior, overwrites, large values, concurrent writes and reads, same-key write races, `findNear` boundary conditions, forward/reverse iteration, seek semantics, and read/write benchmarks against a map baseline.
