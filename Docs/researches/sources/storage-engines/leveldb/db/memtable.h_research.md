# sources/storage-engines/leveldb/db/memtable.h

## Purpose
This header declares `MemTable`, LevelDB's reference-counted mutable in-memory table for recent writes.

## Important APIs, Types, And Functions
Public methods are constructor, `Ref`, `Unref`, `ApproximateMemoryUsage`, `NewIterator`, `Add`, and `Get`. Private types include `KeyComparator` and the skiplist `Table`. The destructor is private to force deletion through `Unref`.

## Control Flow
Callers must increment references before sharing a memtable with readers/iterators/background work and call `Unref` when done. `Add` accepts explicit sequence/type/key/value; `Get` accepts a `LookupKey` built for a snapshot sequence.

## State And Persistence Behavior
Members are comparator, integer refcount, arena allocator, and skiplist. The memtable is volatile but is paired with a WAL during normal DB operation and becomes immutable before being flushed to an SSTable.

## Dependencies And Integration Points
It depends on internal key format, skiplist, public DB types, and arena. `DBImpl`, recovery, write-batch insertion, table building, and iterators use it directly.

## Risks And Edge Cases
Manual non-atomic refcounting assumes external synchronization or single-threaded ownership discipline. Iterators do not keep the memtable alive by themselves; callers must ensure lifetime. Large values increase arena memory until the whole memtable is freed.

## Test Signals
DB-level tests validate memtable behavior through reads before/after flush, immutable-layer reads, recovery, snapshots, approximate memory usage, and compactions.
