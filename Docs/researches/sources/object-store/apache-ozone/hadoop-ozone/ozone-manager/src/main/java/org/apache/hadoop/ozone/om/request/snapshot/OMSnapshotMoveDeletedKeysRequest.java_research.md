
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveDeletedKeysRequest.java

Purpose: Internal request that moves deleted-key metadata from a deleted snapshot toward the next snapshot or active object store during snapshot cleanup.

Important APIs and types: Extends `OMClientRequest`; uses `SnapshotMoveDeletedKeysRequest`, `SnapshotMoveKeyInfos`, `SnapshotInfo`, `SnapshotChainManager`, `SnapshotUtils`, `OMSnapshotMoveUtils`, `OMSnapshotMoveDeletedKeysResponse`, and `FILESYSTEM_SNAPSHOT` layout gating.

Control flow: Validation reconstructs the source snapshot from protobuf, verifies it still exists, finds the next snapshot in the chain, reads lists of keys to move/reclaim/rename and deleted directories, updates source/next snapshot transaction info through `OMSnapshotMoveUtils.updateCache`, resolves bucket object ID, and returns a response carrying all move lists for response-side DB updates.

State and persistence behavior: Directly updates snapshot info cache transaction metadata for source and next snapshots. Actual table-entry movement is represented in the response object.

Dependencies and integration points: Called by internal snapshot cleanup services and integrates with snapshot chain lookup, bucket metadata, and response classes that apply deleted/renamed table mutations.

Risks: No `preExecute` validation of key prefixes or duplicates exists here, unlike `OMSnapshotMoveTableKeysRequest`. Tests should cover source missing, next snapshot absent, bucket ID propagation, cache transaction-info updates, and response-side DB movement.
