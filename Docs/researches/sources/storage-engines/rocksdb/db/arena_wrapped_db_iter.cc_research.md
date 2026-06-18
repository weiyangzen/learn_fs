# sources/storage-engines/rocksdb/db/arena_wrapped_db_iter.cc

## Purpose
Implements `ArenaWrappedDBIter`, the public iterator wrapper that owns an arena and lazily installs the internal iterator tree beneath `DBIter`. It also implements explicit refresh and auto-refresh when superversions change.

## Important APIs and Control Flow
`EnsureInternalIteratorInitialized` builds the internal iterator through `DBImpl::NewInternalIterator`, optionally with bounded MultiScan pruning, clears deferred state, and attaches it to `DBIter`. `Init` normalizes read options, disables async I/O if unsupported, accounts for prefix seek settings, and creates the `DBIter` in the arena. `DoRefresh` destroys the old DBIter/arena, obtains a referenced superversion, refreshes read callbacks, reinitializes DBIter, and installs a new internal iterator. `Refresh` handles same-superversion snapshot sequence changes and mutable-memtable range tombstone refresh; if the superversion changes mid-refresh, it retries with full reinit. `MaybeAutoRefresh` detects relaxed superversion-number changes after seeks or movement and reconciles non-seek cursor position.

## State, Dependencies, and Risks
State includes deferred `SuperVersion`, referenced `ColumnFamilyData`, read options, sequence number, refresh flags, and optional memtable range-tombstone iterator pointer. It depends on DBImpl, ColumnFamilyData locking, DBIter, arenas, snapshots, range tombstones, and filesystem async feature checks. Risks are lifetime-sensitive destructor/manual arena destruction, refresh not preserving `Prepare` scan options, relaxed superversion detection, and consistency subtleties with WritePrepared snapshots. Test signals are iterator refresh, MultiScan, range deletion, and snapshot tests elsewhere.
