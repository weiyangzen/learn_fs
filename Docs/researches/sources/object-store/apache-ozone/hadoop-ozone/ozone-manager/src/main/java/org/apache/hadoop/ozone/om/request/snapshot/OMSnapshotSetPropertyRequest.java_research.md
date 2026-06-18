
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotSetPropertyRequest.java

Purpose: Internal request that updates computed snapshot properties such as exclusive size, replicated size, deep-clean flags, and directory-deep-clean deltas.

Important APIs and types: Extends `OMClientRequest`; uses one or many `SetSnapshotPropertyRequest` protos, `SnapshotInfo`, `SnapshotSize`, `snapshotInfoTable`, `OMSnapshotSetPropertyResponse`, `OmSnapshotInternalMetrics`, and system audit logging.

Control flow: Validation collects singular and repeated property requests, rejects duplicate snapshot keys in one request, loads each snapshot info row, applies optional property fields via `updateSnapshotProperty`, records per-snapshot audit params, writes each updated snapshot to the cache, increments metrics per update, and returns a response containing updated snapshots. IO and unchecked IO failures produce an error response and failure metric.

State and persistence behavior: Mutates snapshot info table cache entries for existing snapshots. It updates snapshot objects in memory before cache insertion.

Dependencies and integration points: Used by background snapshot size/deep-clean computation services and integrates with OM metadata persistence, internal metrics, and system audit.

Risks: Duplicate snapshot keys are rejected to avoid conflicting updates in a single transaction. Error construction for missing snapshots has a malformed message but correct `FILE_NOT_FOUND` code. Tests should cover each optional field, batch updates, duplicate detection, missing snapshot, and audit payloads.
