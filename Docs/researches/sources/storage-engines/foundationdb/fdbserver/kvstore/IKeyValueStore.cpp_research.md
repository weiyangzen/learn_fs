# sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueStore.cpp

## Purpose
`IKeyValueStore.cpp` implements the central factory `openKVStore(...)`, mapping `KeyValueStoreType` enum values to concrete storage-engine constructors. It is a dispatch layer, not a storage implementation.

## Important APIs, Types, and Functions
The only function defined here is `openKVStore(...)`. It accepts store type, filename, log ID, memory limit, checksum/integrity flags, database info, and page-cache bytes, then returns an `IKeyValueStore*` from one of the backend helper constructors declared in `IKeyValueStore.h`.

## Control Flow
The switch dispatches SQLite B-tree V1/V2, memory, Redwood, RocksDB, sharded RocksDB, and memory radix-tree stores. V1 SQLite disables checksums, V2 forwards checksum and integrity options, Redwood receives database info and page-cache bytes, and `MEMORY_RADIXTREE` reuses `keyValueStoreMemory` with extension `"fdr"` and type `MEMORY_RADIXTREE`.

## State and Persistence Behavior
This file owns no persistent state. Persistence behavior is selected by backend: memory stores use a disk queue log, SQLite/RocksDB/Redwood persist to their own formats, and checksum/integrity flags are forwarded only to supporting backends.

## Dependencies and Integration Points
It includes `ServerDBInfo`, `IKeyValueStore.h`, and Flow basics. Storage server initialization and tests use this factory when opening stores from configuration.

## Risks
Adding a new `KeyValueStoreType` requires updating this switch. Backend-specific parameters are intentionally uneven, so incorrect dispatch can silently choose a different on-disk format, extension, or checksum policy.

## Test Signals
There are no local tests. Signals come from backend open/recovery tests for each `KeyValueStoreType` and compile-time pressure when new enum values are added.
