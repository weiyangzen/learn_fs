# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/DBStoreBuilder.java

## Purpose
`DBStoreBuilder` constructs `RDBStore` instances by combining DB definitions, metadata paths, RocksDB profile defaults, optional `.ini` configuration, metrics/statistics settings, WAL/log settings, read-only mode, checkpoint directory behavior, and optional compaction-DAG differ support.

## Important APIs and Types
Static entry points are `createDBStore` and several `newBuilder` overloads. Builder methods include `setName`, `setPath`, `setOptionsPath`, `addTable`, `setDBOptions`, `setDefaultCFOptions`, `setOpenReadOnly`, `setEnableCompactionDag`, `setCreateCheckpointDirs`, `setEnableRocksDbMetrics`, `setProfile`, `setMaxNumberOfOpenFiles`, and `disableDefaultCFAutoCompaction`. `build` returns an `RDBStore`.

## Control Flow and State
Construction reads config for statistics, CF write buffer size, default DB profile, RocksDB configuration, and max DB update size. Applying a `DBDefinition` sets name/path/options path and adds all column families, preferring file-based CF options, then definition-level options. `build` validates required fields, creates table configs, selects DB options, applies statistics and write options, checks parent directory, and constructs `RDBStore`.

## Persistence, Dependencies, and Integration
The builder creates/open RocksDB stores and thus controls persistent DB layout. It depends on HDDS config keys, `DBConfigFromFile`, `DBProfile`, managed RocksDB options/statistics/write options/loggers, `RocksDBConfiguration`, and `RDBStore`.

## Risks and Test Signals
Native option ownership is delicate: `tableConfigs` are closed in `finally`, while DB options/statistics/write options transfer to `RDBStore` on success and are closed on failure. The default CF is always added. Tests should cover missing name/path, nonexistent parent directory, read-only builds, `.ini` precedence, profile fallback, statistics off/on, logger settings, max open files, compaction DAG lock requirements, metrics disabling, and cleanup on constructor failure.
