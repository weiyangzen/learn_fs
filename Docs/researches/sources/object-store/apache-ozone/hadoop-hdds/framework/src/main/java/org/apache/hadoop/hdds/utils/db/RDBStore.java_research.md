# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStore.java

## Purpose
`RDBStore` is the concrete RocksDB-backed implementation of `DBStore`. It opens RocksDB with configured column families, exposes raw and typed tables, manages checkpoints/snapshots, flush/compact/drop operations, Metrics2 registration, optional compaction-DAG checkpoint differ integration, and WAL delta retrieval for Recon.

## Important APIs and Types
Constructor parameters include DB file, DB options/statistics/write options, table configs, read-only flag, metrics name, compaction DAG settings, delta size threshold, checkpoint dir flag, configuration, and metrics enable flag. Public APIs implement table access, compaction, close, `getCheckpoint`, `getSnapshot`, `getUpdatesSince`, property reads, metrics access, and checkpoint differ access.

## Control Flow and State
Construction optionally initializes `RocksDBCheckpointDiffer`, opens `RocksDatabase`, registers `RocksDBStoreMetrics`, creates checkpoint/snapshot parent directories, wires differ column-family handles, loads compaction logs, creates `RDBCheckpointManager`, and registers `RDBMetrics`. `close` unregisters metrics, closes checkpoint/differ/statistics resources, flushes non-read-only DBs, and closes RocksDB. `getUpdatesSince` validates WAL availability, skips old batches, enforces count and cumulative size limits, closes each write batch, updates metrics, and throws `SequenceNumberNotFoundException` when full deltas are unavailable.

## Persistence, Dependencies, and Integration
This class owns the live RocksDB database, checkpoint directories, snapshot directories, WAL reads, table handles, metrics, and compaction differ state. It depends on `RocksDatabase`, managed RocksDB options/statistics/write options, `RDBCheckpointManager`, `RDBMetrics`, `RocksDBStoreMetrics`, Ozone snapshot constants, and `RocksDBCheckpointDiffer`.

## Risks and Test Signals
Constructor failure calls `close`, but final fields such as `checkPointManager` may be uninitialized on early failures depending on Java initialization path. `dropTable` permanently removes column families. Global `RDBMetrics.unRegister` on close can affect other stores. WAL delta logic must handle sequence gaps accurately to trigger full snapshot fallback. Tests should cover open/close success and failure cleanup, read-only close no-flush, checkpoint/snapshot dirs disabled, metrics enable/disable, compaction DAG required CFs, table not found, batch commit, flush/compact/drop, getUpdatesSince sequence gaps/limits/size threshold/latest sequence, and multiple-store metrics interactions.
