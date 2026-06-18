<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotPurgeResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotPurgeResponse.java

Purpose: Finalizes snapshot purge by updating related snapshot metadata, invalidating snapshot cache state, recording local purge transaction info, deleting checkpoint directories, and removing purged snapshot info rows.

Important APIs/types/functions: Extends `OMClientResponse`. The success constructor stores snapshot DB keys to purge, updated snapshot infos, and `TransactionInfo`; failure constructor initializes fields to null after `checkStatusNotOK()`. Helpers are `updateSnapInfo` and `updateLocalData`.

Control flow and persistence: It first writes `updatedSnapInfos` to `SnapshotInfoTable`. For each purge key, it reads snapshot info with `getSkipCache`, skips missing entries, invalidates `OmSnapshotManager` cache, removes snapshot ID mapping from chain manager, writes purge transaction info to snapshot local data through `WritableOmSnapshotLocalDataProvider`, deletes checkpoint directories, and batches deletion of the snapshot info row.

Dependencies and integration: Used by snapshot purge requests, snapshot deletion service, snapshot cache, chain manager, local data manager, and checkpoint directory management.

Risks and test signals: Purge has filesystem side effects plus DB state updates. Tests should cover missing snapshot info, cache invalidation, chain map removal, local data transaction update, checkpoint directory deletion, updated neighboring snapshot info, and retry after partially deleted directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotPurgeResponse.java -->
