<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl.go -->
# sources/storage-engines/pebble/internal/arenaskl/skl.go

## Purpose
This file implements Pebble's concurrent arena-backed skiplist used by memtables.

## Important APIs, Types, And Functions
`Skiplist` owns the arena, comparer, head/tail nodes, height, and testing flag. `Inserter` caches splices for sequential insertion. Key methods include `NewSkiplist`, `Reset`, `Add`, `Inserter.Add`, `NewIter`, `NewFlushIter`, `newNode`, `randomHeight`, `findSplice`, `findSpliceForLevel`, `keyIsAfterNode`, `getNext`, and `getPrev`.

## Control Flow
Insertion finds per-level splices, allocates a random-height node, raises list height with CAS, and inserts bottom-up by CASing next offsets before prev offsets. On races it helps repair stale prev links and recomputes the affected splice.

## State And Persistence Behavior
State is in arena memory and atomic offsets. Nodes are immutable after insertion; deletion is represented by higher-level tombstones, not physical removal. The inserter cache is caller-local and invalidated on concurrent interference.

## Dependencies And Integration Points
It depends on `base.Compare`, arena/node internals, `math/rand/v2`, atomics, runtime scheduling for race amplification, and skiplist iterators. Pebble memtables rely on it for ordered internal keys.

## Risks And Edge Cases
Concurrent insertion has an intermediate state where forward and backward links disagree. Duplicate internal keys return `ErrRecordExists`. Correct ordering depends on user-key compare plus descending trailer order.

## Test Signals
`skl_test.go` covers empty/full lists, duplicates, concurrency, iterator behavior, bounds, strict-prefix iteration, splice correctness, and benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/skl.go -->
