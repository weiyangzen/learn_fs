
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotPurgeRequest.java

Purpose: Internal final purge request that removes deleted snapshots from the snapshot table and chain while updating neighboring snapshots for deeper cleanup.

Important APIs and types: Extends `OMClientRequest`; uses `SnapshotPurgeRequest`, `SnapshotInfo`, `SnapshotChainManager`, `SnapshotUtils`, `TransactionInfo`, `updatedSnapshotInfos`, `OMSnapshotPurgeResponse`, `OmSnapshotInternalMetrics`, and system audit logging.

Control flow: For each requested snapshot DB key, validation loads the latest snapshot info from a local map/table, skips already-purged rows, finds next and next-to-next snapshots, clears deep-clean flags on them, updates chain predecessor links for next path/global snapshots, tombstones the purged snapshot row, removes it from local cache, then stamps all updated snapshots with the current transaction info and returns a purge response.

State and persistence behavior: Writes cache updates for affected neighbor snapshots, deletes purged snapshot rows via tombstone cache entries, mutates in-memory `SnapshotChainManager`, and carries updated snapshots in the response.

Dependencies and integration points: Called by snapshot deleting service and coordinates with chain state, deep-cleaning services, snapshot info table persistence, internal metrics, and system audit.

Risks: The request relies on serialized OM state machine execution rather than explicit locks. It tolerates `NoSuchElementException` when a snapshot was already removed from in-memory chain but not flushed. Tests should cover multi-snapshot purge ordering, chain predecessor rewrites, deep-clean flag resets, already-purged rows, and last-transaction-info updates.
