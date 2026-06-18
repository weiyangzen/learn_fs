# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyPurgeResponse.java

Purpose: `OMKeyPurgeResponse` permanently removes deleted-table entries after block cleanup and handles snapshot-related movement/update metadata.

Important APIs and types: It stores purge key list, snapshot renamed key list, optional source `SnapshotInfo`, optional `SnapshotMoveKeyInfos`, and bucket infos to update. It uses snapshot manager, snapshot DB batches, deleted table, snapshot renamed table, and snapshot info table.

Control flow: With a source snapshot, it acquires a snapshot DB content read lock, opens the snapshot metadata DB batch, deletes purge keys and renamed entries there, writes replacement repeated key infos, commits the snapshot batch, and updates active snapshot info. Without a snapshot it performs the same key processing in active metadata. It then writes bucket updates.

State and persistence behavior: It deletes from deleted table, deletes snapshot rename markers, may rewrite deleted-table entries, updates snapshot info, and writes bucket quota state.

Dependencies and integration points: It integrates `OMKeyPurgeRequest`, key deleting service, snapshot move-deleted-keys logic, and bucket accounting.

Risks and test signals: Risks include cross-DB partial commits, snapshot lock failure, and null `keysToUpdateList`. Tests should cover active and snapshot purge, renamed marker deletion, bucket updates, and replacement repeated key info.
