## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManagerImpl.java

Purpose: concrete `SnapshotDiffMetadataManager` backed by a `DBStore`, responsible for opening the snapshot diff DB and exposing typed table handles.

Important APIs and types: constructor takes `ConfigurationSource`; getters return typed `Table` instances; `close` closes `dbStore`. It uses `DBStoreBuilder`, `DBStoreBuilder.getDBDirPath`, `PARTIAL_CACHE`, and table definitions from `SnapshotDiffDBDefinition`.

Control flow: constructor computes the DB path, checks `VERSION`, deletes the entire DB directory when the content is absent or not equal to `"1"`, builds the DB store, opens each table with partial cache, and writes the version file when a new DB is created.

State and persistence: owns the snapshot diff RocksDB directory and a plain `VERSION` file. Persistence includes jobs, reports, purged jobs, and intermediate object tables.

Dependencies and integration: used by OM snapshot diff initialization and cleanup components. Its destructive version mismatch behavior is the operational boundary for incompatible schema upgrades.

Risks and edge cases: missing `VERSION` is treated as mismatch and deletes an existing DB path, which is acceptable only if old data is intentionally disposable or incompatible. Version file write happens after DB open; failures can leave a recreated DB without a version. Tests should cover new DB creation, matching-version open preserving data, mismatched-version deletion, missing-version behavior, table codec round trips, and close idempotence expectations.
