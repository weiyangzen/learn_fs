# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBCheckpointManager.java

## Purpose
`RDBCheckpointManager` wraps RocksDB checkpoint creation and translates it into HDDS `RocksDBCheckpoint` objects with metadata such as creation time and latest sequence number.

## Important APIs and Types
The constructor stores a `RocksDatabase`, checkpoint name prefix, and `RocksCheckpoint`. `createCheckpoint(parentDir, name)` creates a named or timestamped checkpoint. `createCheckpoint(parentDir)` uses the default timestamp naming scheme. `close` closes the underlying Rocks checkpoint object.

## Control Flow and State
Checkpoint creation builds a directory name from optional prefix and supplied name or `checkpoint_<time>`, flushes WAL and memtables, calls RocksDB checkpoint creation, reads latest sequence number, measures elapsed time, waits for the directory to exist, and returns a `RocksDBCheckpoint`. IO failures are logged and return null.

## Persistence, Dependencies, and Integration
It writes checkpoint directories under the supplied parent path and depends on `RocksDatabase.RocksCheckpoint`, `RocksDBCheckpoint`, and `RDBCheckpointUtils`. It is owned by `RDBStore`.

## Risks and Test Signals
Returning null on `IOException` rather than throwing can push failure handling to callers. Directory existence waiting is best-effort. Tests should cover naming, explicit names, flush ordering, latest sequence propagation, creation duration, missing parent behavior, null return on IO failure, and close lifecycle.
