# sources/storage-engines/rocksdb/memtable/skiplist.h

## Purpose
`skiplist.h` defines the older generic `SkipList<Key, Comparator>` template derived from LevelDB. It is used where keys are stored separately from nodes, including bucket skiplists in hash-based memtable reps.

## Important APIs, Types, and Functions
- `SkipList(Comparator, Allocator*, max_height, branching_factor)` creates a head node, initializes relaxed `max_height_`, and allocates the predecessor cache `prev_`.
- `Insert(const Key&)` inserts a unique key with external synchronization.
- `Contains`, `Iterator::{Seek, SeekForPrev, Next, Prev, SeekToFirst, SeekToLast}` provide lookup and traversal.
- `ApproximateNumEntries(start_ikey, end_ikey)` estimates range size from sampled skiplist levels.
- `Node` stores `Key const key` and a flexible array of atomic next pointers.

## Control Flow
Search starts from the current top height and descends, reusing the last comparison result through `last_bigger`/`last_not_after`. `Insert()` has a fast path for sequential insertion using cached predecessors. If the cached predecessor does not bracket the new key, `FindLessThan()` recomputes all predecessors. Random height follows the configured branching factor, and raising `max_height_` uses relaxed storage because readers seeing either old or new head-level links remain correct. Links are initialized relaxed in the new node and published via release stores from predecessors.

## State and Persistence Behavior
Nodes are allocated from the provided allocator and never deleted individually. The skiplist only stores pointers and key copies/references in memory; it persists nothing. Reads can run concurrently with a single externally synchronized writer, provided the list outlives readers.

## Dependencies and Integration Points
The template depends on `Allocator`, RocksDB atomics, `Random`, and port utilities. `hash_skiplist_rep.cc` and promoted buckets in `hash_linklist_rep.cc` instantiate it for `const char*` memtable keys.

## Risks and Test Signals
Writes require external synchronization, unlike `InlineSkipList`'s CAS insertion path. Duplicate insertion is guarded by debug asserts. The visible `ApproximateNumEntries()` implementation calls `next->Key()`, but this `Node` type exposes the key as `key` and does not define `Key()`, making this path suspicious unless hidden compatibility exists elsewhere; consumers should verify compilation for instantiations using that method. `skiplist_test.cc` covers empty behavior, random insert/lookup, forward/backward iteration, and concurrent reader/single-writer visibility.
