# sources/storage-engines/badger/level_handler.go

## Purpose
`level_handler.go` manages one LSM level's table set, size accounting, table replacement/deletion, point lookup, iterator construction, and overlap calculations. It is a core part of Badger's levels controller and compaction/read paths.

## Important APIs, Types, and Functions
- `levelHandler`: synchronized table slice, total size, stale size, level number/string, and DB pointer.
- Size/lifecycle: `isLastLevel`, `getTotalStaleSize`, `getTotalSize`, `initTables`, `close`.
- Mutation: `deleteTables`, `replaceTables`, `addTable`, `sortTables`, `tryAddLevel0Table`, `addSize`, `subtractSize`, `decrRefs`.
- Query/read: `numTables`, `getTableForKey`, `get`, `appendIterators`.
- Overlap: `levelHandlerRLocked`, `overlappingTables`.

## Control Flow and State
Level 0 tables are sorted by file id/time and may overlap; newer tables are considered first for reads. Levels >=1 are sorted by smallest key and assumed non-overlapping. Mutations copy or rebuild table slices so iterators can safely keep previous slices. `replaceTables` increments refs for new tables, sorts, unlocks, then decrements removed refs to avoid holding locks during slow close/delete work.

## Persistence Behavior
The handler itself is in-memory, but it owns references to persisted SST files. It must be updated in coordination with manifest changes elsewhere; comments note removed tables should only be dereferenced after manifest updates are durable. Size and stale-size counters reflect table metadata used for compaction decisions.

## Dependencies and Integration Points
Used by `levelsController`, compaction, DB loading, `DB.get`, and iterator construction. Depends on `table.Table`, table iterators, Badger `y` key comparison/hash/metrics helpers, and `IteratorOptions`.

## Risks and Edge Cases
Correctness depends on preserving L0 recency ordering and non-overlap ordering for lower levels. Refcount increments/decrements are critical for safe concurrent iterators and compactions. `getTableForKey` for levels >=1 returns the first table whose biggest key is >= target without explicitly verifying smallest <= key, relying on iterator seek to miss if not contained.

## Test Signals
`TestCompactionFilePicking` directly manipulates level handlers and compaction sort behavior. Many DB/iterator/load tests indirectly cover table replacement, point lookup, iterator appending, and close paths.
