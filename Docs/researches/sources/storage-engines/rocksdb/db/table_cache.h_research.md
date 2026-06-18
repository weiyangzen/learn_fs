# sources/storage-engines/rocksdb/db/table_cache.h

## Purpose

`table_cache.h` declares `TableCache`, a thread-safe wrapper over cached SST `TableReader` objects and row cache access. It hides file opening, table-reader construction, cache-handle lifetime, range tombstone access, and table property helpers behind a column-family scoped API.

## Important APIs, Types, and Functions

`TableCacheOpenOptions` controls ephemeral table readers, shared metadata cache avoidance, and filter skipping. `TableCache` exposes `NewIterator`, `Get`, `GetRangeTombstoneIterator`, `MultiGetFilter`, sync/async `MultiGet`, static `Evict`/`ReleaseObsolete`/`Lookup`, `FindTable`, `GetTableProperties`, `ApproximateKeyAnchors`, memory usage, approximate offset/size, `get_cache`, `file_options`, `SetTablesAreImmortal`, `UpdateShouldPinTableHandles`, and `SetFastSstOpen`. Type aliases wrap typed cache handles for table readers and row cache strings.

## Control Flow

Most public operations resolve a `TableReader` through `FindTable`, then delegate to table-reader methods. `NewIterator` returns an `InternalIterator` whose cleanup releases any cache handle. `Get` and `MultiGet` optionally consult row cache before table I/O. Static cache helpers are used by obsolete-file cleanup paths that may not have a full `TableCache` instance.

## State and Persistence Behavior

The class stores immutable options, copied file options, typed cache interface, row-cache id, immortality/pinning flags, relaxed-atomic fast-SST-open flag, block/IO tracers, striped loader mutexes, and session id. It does not own durable SST metadata but it uses `FileMetaData` and `FileDescriptor` fields, including pinned readers and file-open metadata.

## Dependencies and Integration Points

The header depends on cache, DB format, range deletion, CF options, public env/options/table APIs, table readers, block cache tracing, and coroutine utilities. It is owned by `ColumnFamilyData`, used by read paths, compaction setup, `VersionBuilder::LoadTableHandlers`, and DB metadata/property queries.

## Risks and Test Signals

Risks include caller misuse of `open_ephemeral_table_reader` with `table_reader_ptr` or no-IO reads, stale `should_pin_table_handles_` after cache capacity changes, filter skipping changing correctness, and static cache erasure conflicting with concurrent users. Tests should cover every documented ownership contract, cache-capacity transitions, pinning behavior, range deletion iterator ownership, and both sync and coroutine MultiGet declarations.
