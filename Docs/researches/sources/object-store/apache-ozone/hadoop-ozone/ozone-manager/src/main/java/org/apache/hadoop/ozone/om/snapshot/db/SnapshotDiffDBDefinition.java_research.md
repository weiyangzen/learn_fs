## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffDBDefinition.java

Purpose: defines the RocksDB schema for the standalone snapshot diff database.

Important APIs and types: singleton `SnapshotDiffDBDefinition.get()` extends `DBDefinition.WithMap`; names the DB via `OM_SNAPSHOT_DIFF_DB_NAME` and location config key `OZONE_OM_SNAPSHOT_DIFF_DB_DIR`. Column families include `snap-diff-job-table`, `snap-diff-report-table`, `snap-diff-purged-job-table`, and intermediate `-from-snap`, `-to-snap`, `-unique-ids`.

Control flow and persistence: the class builds an immutable CF map with codecs for `SnapshotDiffJob`, `DiffReportEntry`, `Long`, `SnapshotDiffObjectInfo`, and `Boolean`. Intermediate CF definitions are schema names, while runtime code prefixes them with job IDs for temporary per-job tables.

Dependencies and integration: consumed by `SnapshotDiffMetadataManagerImpl` and `SnapshotDiffManager` when creating/dropping temporary column families. Diff report entries use `SnapshotDiffReportOzone.getDiffReportEntryCodec`.

Risks and test signals: schema changes require versioning in `SnapshotDiffMetadataManagerImpl`; codec compatibility is critical for persisted jobs and reports. Tests should verify CF names, codecs, immutable map contents, DB name/location config, and that temporary CF suffixes match manager expectations.
