# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStore.java

## Purpose
`DBStore` is the main abstraction for HDDS metadata databases that expose named tables, typed table access, batch operations, flush/compact/checkpoint operations, WAL delta reads, and lifecycle management.

## Important APIs and Types
Key methods include raw and typed `getTable`, `listTables`, `flushDB`, `flushLog`, `compactDB`, `compactTable`, `getEstimatedKeyCount`, `getCheckpoint`, `getDbLocation`, `getTableNames`, `dropTable`, `getUpdatesSince`, `isClosed`, `getSnapshotsParentDir`, and `getRocksDBCheckpointDiffer`.

## Control Flow and State
The interface extends `UncheckedAutoCloseable` and `BatchOperationHandler`. Default typed `getTable` uses `CacheType.PARTIAL_CACHE`, while implementations provide actual backend behavior.

## Persistence, Dependencies, and Integration
This interface represents persistent metadata stores and integrates with RocksDB-specific classes, table cache types, compaction options, checkpoint diffing, and Recon delta update flows.

## Risks and Test Signals
Some methods are RocksDB-specific despite the generic name, such as checkpoint differ and RocksDB exceptions. `dropTable` is destructive. Tests should use implementation suites to verify table typing, checkpoint creation, WAL delta limits, compaction, read-only close behavior, and lifecycle after close.
