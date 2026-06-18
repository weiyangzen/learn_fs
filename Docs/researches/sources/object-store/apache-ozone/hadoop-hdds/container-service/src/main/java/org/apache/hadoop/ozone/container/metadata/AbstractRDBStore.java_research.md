## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractRDBStore.java

Purpose: Provides the generic RocksDB-backed store manager base used by datanode metadata stores.

Important APIs and functions: The constructor selects `DatanodeDBProfile`, reads DB and column-family options from configured files when present, applies create-if-missing and log settings, and delegates DB construction to `initDBStore()`. `stop()`, `close()`, `isClosed()`, `getStore()`, `getBatchHandler()`, `flushDB()`, `flushLog()`, and `compactDB()` implement `DBStoreManager`.

Control flow and state: Each instance owns a `DBDefinition`, shared/default column-family options, and a volatile `DBStore`. `close()` stops the store then closes CF options. `dbProfile` is static, so the last constructed store updates the class-wide profile reference.

Persistence and dependencies: It directly opens and manages RocksDB through HDDS `DBStoreBuilder`, managed RocksDB options, `DBConfigFromFile`, and datanode configuration log settings. Subclasses choose column families and expose typed tables.

Risks: Static `dbProfile` can surprise tests with multiple configurations. File-based RocksDB option parsing failures abort store construction. `cfOptions` is closed on `close()`, so no table should outlive the store. A null options file falls back to profile defaults.

Test signals: Cover construction with default and file-based DB/CF options, read-only open, log level/file settings, close/stop idempotence, flush/compact delegation, DB profile exposure, and option-file exception handling.
