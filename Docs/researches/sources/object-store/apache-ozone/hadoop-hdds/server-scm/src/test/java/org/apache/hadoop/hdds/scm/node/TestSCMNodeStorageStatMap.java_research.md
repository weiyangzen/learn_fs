# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestSCMNodeStorageStatMap.java

Purpose: tests `SCMNodeStorageStatMap`, the datanode-to-volume usage map used by SCM node accounting.

Important APIs and types: uses `SCMNodeStorageStatMap`, `StorageLocationReport`, `StorageReportProto`, `NodeReportProto`, `StorageType`, utilization thresholds, and `StorageReportResult`. Test data is a `ConcurrentHashMap<UUID, Set<StorageLocationReport>>` of 100 datanodes with one DISK volume each.

Control flow: setup generates test data. Tests validate known-node lookup, duplicate insert rejection, update of unknown datanodes, processing of single-node reports, and aggregate behavior after bulk inserts, updates, threshold queries, and removals. Single-node report flow starts with matching storage, adds a full storage report to trigger out-of-space, then adds a failed full disk to trigger combined failed-and-out-of-space status.

State and persistence behavior: state is entirely in-memory inside `SCMNodeStorageStatMap`. Inserts, updates, report processing, and removals mutate volume sets and aggregate total capacity/free/used counters. Threshold queries classify datanodes as normal, warn, or critical according to the updated utilization.

Dependencies and integration points: depends on Ozone constants for GB units, HDDS test report builders, storage protobuf conversion from `StorageLocationReport`, and `SCMException` messages for invalid operations.

Risks and edge cases: generated datanode UUID keys differ from the storage report IDs in `generateData`, so the test focuses on map behavior rather than ID consistency between key and volume. Some assertions use floating-point arithmetic for expected counts. The single-node test includes a builder variable used only to assemble a final report.

Test signals: good coverage for map membership, duplicate protection, unknown update errors, report status classification, aggregate counter updates, threshold list sizes, and removal behavior.
