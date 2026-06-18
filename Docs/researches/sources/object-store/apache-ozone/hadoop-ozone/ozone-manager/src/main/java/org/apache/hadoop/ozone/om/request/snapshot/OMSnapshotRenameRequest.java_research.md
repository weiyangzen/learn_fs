
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotRenameRequest.java

Purpose: Renames an active snapshot by moving its snapshot info table key and updating chain metadata.

Important APIs and types: Extends `OMClientRequest`; uses `RenameSnapshotRequest/Response`, `SnapshotInfo`, `BUCKET_LOCK`, two `SNAPSHOT_LOCK`s, snapshot rename config keys, feature/layout annotations, and `OMSnapshotRenameResponse`.

Control flow: `preExecute` checks server config allows rename, validates new snapshot name, resolves linked buckets, checks bucket owner/admin permission, and writes a leader-generated rename time. Validation locks the bucket and both old/new snapshot names, rejects new-name collision, loads old snapshot, rejects missing/deleted/non-active states, changes the name, tombstones the old table key, adds the new table key, updates `SnapshotChainManager`, builds a response, releases locks, and audits.

State and persistence behavior: Deletes the old snapshot info table row and adds the renamed row at the transaction index. The same `SnapshotInfo` object is also reflected in the in-memory snapshot chain.

Dependencies and integration points: Integrates snapshot feature flag/config, linked bucket resolution, authorization, snapshot locks, chain manager update, audit, and metrics.

Risks: `renameTime` is generated but not used in validation in this file. Lock ordering on old/new names must be consistent with other snapshot operations. Tests should cover config-disabled behavior, name collision, deleted snapshot rename, old/new table cache updates, and chain lookup after rename.
