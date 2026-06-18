<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/skl/arena.go -->
# sources/storage-engines/badger/skl/arena.go

## Purpose
This file implements the lock-free byte arena used by Badger's skiplist. It allocates nodes, keys, and encoded values from a contiguous byte slice and uses integer offsets instead of Go pointers for compact storage.

## Important APIs, Types, And Functions
`Arena` holds an atomic allocation cursor and backing buffer. Constants `offsetSize` and `nodeAlign` support node tower sizing and 64-bit alignment. `newArena`, `size`, `putNode`, `putVal`, `putKey`, `getNode`, `getKey`, `getVal`, and `getNodeOffset` allocate and decode skiplist arena data.

## Control Flow
Allocation methods atomically add the required byte count to the cursor, assert the new total fits the buffer, and return the starting offset. `putNode` overallocates by alignment padding, subtracts unused tower slots for shorter nodes, and returns an aligned offset. `putVal` encodes a `y.ValueStruct` into the buffer. `putKey` copies key bytes. Getters slice the buffer or convert an aligned offset back to a `*node` via `unsafe.Pointer`.

## State And Persistence Behavior
Arena state is process memory only and is not persisted directly. WAL replay and normal writes repopulate skiplists into arenas. Offset zero is reserved as nil, so allocations start at one.

## Dependencies And Integration Points
It depends on `sync/atomic`, `unsafe`, and `y.ValueStruct` encoding. It is used by `skl.Skiplist`, which is used by `memTable` for write buffering and recovery.

## Risks And Edge Cases
The arena relies on unsafe pointer conversion and correct 64-bit alignment for atomic loads from node values. It panics via assertions on arena exhaustion rather than returning allocation errors. Returned key/value slices alias the arena buffer and must not outlive the skiplist. Node offset calculation assumes the node pointer belongs to the arena buffer.

## Test Signals
No direct arena test is included in this subset. Indirect signals come from memtable/skiplist behavior across writes, reads, WAL replay, and concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/skl/arena.go -->
