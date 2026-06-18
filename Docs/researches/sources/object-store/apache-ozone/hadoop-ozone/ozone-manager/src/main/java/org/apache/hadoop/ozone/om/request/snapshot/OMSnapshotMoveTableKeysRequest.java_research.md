
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveTableKeysRequest.java

Purpose: Internal request that validates and moves deleted-key, deleted-directory, and rename-table entries from one snapshot to the next active snapshot or AOS.

Important APIs and types: Extends `OMClientRequest`; uses `SnapshotMoveTableKeysRequest`, `SnapshotMoveKeyInfos`, `HddsProtos.KeyValue`, `SnapshotUtils`, `SnapshotChainManager`, `OMSnapshotMoveUtils`, `OmSnapshotInternalMetrics`, and system audit logging.

Control flow: `preExecute` resolves the source snapshot by ID, filters empty deleted-key and invalid deleted-dir entries, validates each key starts with the expected table/bucket prefix, rejects duplicates per category, logs system audit failures in debug mode, and rewrites the request with sanitized lists. Validation reloads the source snapshot, finds the next snapshot, rejects a non-active next snapshot, updates source/next snapshot transaction metadata, returns a response containing move lists and bucket object ID, updates metrics, and emits debug system audit details.

State and persistence behavior: Updates snapshot info cache transaction metadata; actual key/dir/rename table movement is handled by `OMSnapshotMoveTableKeysResponse`.

Dependencies and integration points: Integrates snapshot diff/cleanup services, OM metadata table prefix conventions, FSO deleted-dir tables, system audit, metrics, and snapshot chain traversal.

Risks: Prefix validation is critical to prevent cross-bucket or cross-table moves. The method relies on debug-enabled audit for detailed lists. Tests should cover duplicate detection, prefix rejection, list filtering, non-active next snapshot rejection, no-next-snapshot AOS path, and metrics on success/failure.
