## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManager.java

Purpose: interface for accessing snapshot diff metadata tables.

Important APIs and types: extends `AutoCloseable` and exposes getters for job, report, purged-job, from-snapshot object-info, to-snapshot object-info, and unique-object-id tables.

Control flow and state: no implementation; it defines the table access contract used by callers that should not depend directly on `DBStore`.

Dependencies and integration: tied to `SnapshotDiffDBDefinition`, Hadoop `Table`, `SnapshotDiffJob`, HDFS `DiffReportEntry`, and `SnapshotDiffObjectInfo`.

Risks and test signals: implementations must return tables with codecs matching the DB definition and must close the backing store. Interface-level tests are minimal; integration tests should instantiate the implementation and round-trip every table type.
