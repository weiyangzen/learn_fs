# sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.h

## Purpose
Declares `ArenaWrappedDBIter`, an `Iterator` implementation that wraps `DBIter` plus an arena so the iterator hierarchy can be allocated compactly and lazily.

## Important APIs and Types
The class forwards the public iterator API (`Seek`, `Next`, `Prev`, `key`, `value`, `columns`, `status`, `timestamp`, `PrepareValue`) to the inner `DBIter` after ensuring the internal iterator exists. `Init` constructs DBIter from immutable/mutable CF options, version, sequence, callback, CF handle, blob-index exposure, refresh allowance, and active memtable. `StoreDeferredInitInfo` references the column family, remembers `SuperVersion`, sequence, and flush-mark permission for lazy internal iterator creation. `Refresh`, `Refresh(snapshot)`, `Prepare`, `SetIterUnderDBIter`, and property access provide advanced behavior.

## State, Dependencies, and Risks
The header owns an `Arena`, raw `DBIter*`, refresh metadata, deferred DB state, read options, and range-tombstone iterator pointer. `ColumnFamilyDataUnrefDeleter` unrefs under DB mutex. Risks include requiring `DestroyDBIter` in the destructor, invalid state when deferred DB state is missing, and users calling methods after failed initialization. Integration points are DB iterator creation, SstFileReader, MultiScan, snapshots, blob-index exposure, and auto-refresh iterator support.
