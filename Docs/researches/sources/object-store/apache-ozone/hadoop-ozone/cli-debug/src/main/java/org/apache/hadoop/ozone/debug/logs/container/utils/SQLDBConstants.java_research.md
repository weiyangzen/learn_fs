# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/SQLDBConstants.java

Purpose: `SQLDBConstants` centralizes SQLite driver settings, table names, batch/cache sizes, lifecycle/health state constants, DDL, DML, query SQL, and index SQL for the container log database.

Important APIs and types: Constants include `DEFAULT_DB_FILENAME`, `DRIVER`, `CONNECTION_PREFIX`, `CACHE_SIZE`, `BATCH_SIZE`, table names, create/drop/insert SQL, latest-state queries, health queries, and replication queries. It imports `HddsProtos` and `ContainerHealthState` to derive state strings.

Control flow: There is no runtime flow beyond static constant initialization. The private constructor prevents instantiation.

State and persistence behavior: These strings define the SQLite schema and therefore the persisted shape of parsed container-log diagnostics. The latest table uses a `(datanode_id, container_id)` primary key and `INSERT OR REPLACE`.

Dependencies and integration points: `ContainerDatanodeDatabase` uses every major SQL constant. The queries encode assumptions about latest timestamps, state names, deleted replicas, and a hard-coded quasi-closed threshold of at least three replicas.

Risks: SQL is assembled with string replacement for the replication operator; current callers restrict it but the pattern is brittle. The quasi-closed query uses `>= 3` instead of the configurable default replication factor. Latest-state joins may duplicate rows if multiple events share an identical timestamp.

Test signals: Tests should verify table creation, primary-key replacement, index creation, latest selection, state string compatibility, hard-coded threshold behavior, and operator replacement.
