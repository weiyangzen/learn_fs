# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMDirectoriesPurgeResponseWithFSO.java

Purpose: `OMDirectoriesPurgeResponseWithFSO` persists recursive purge work for deleted FSO directories, moving subdirectories and files through deleted tables and optionally operating against a snapshot DB.

Important APIs and types: It stores `PurgePathRequest` list, bucket update map, optional `SnapshotInfo`, and open-key info map. It uses snapshot manager, `SNAPSHOT_DB_CONTENT_LOCK`, `DBStore` batch operations, `DeletedDirTable`, `DeletedTable`, directory/file tables, and `OmUtils.prepareKeyForDelete`.

Control flow: `addToDBBatch` opens a snapshot DB and write batch when purging from a snapshot, otherwise uses active metadata. `processPaths` moves marked subdirectories to deleted-dir table, deletes directory entries, moves deleted subfiles to deleted table, rewrites open-key metadata, deletes the visited deleted-dir marker, and updates active bucket quota state.

State and persistence behavior: It can mutate both active DB and snapshot DB in one response path. It updates deleted-dir, deleted, directory, file, open-key/open-file, snapshot-info, and bucket tables depending on inputs.

Dependencies and integration points: It integrates directory deletion service, snapshot lifecycle, FSO object-ID keying, bucket quota updates, and asynchronous key deletion.

Risks and test signals: Risks include two-DB atomicity limits, lock acquisition failure, open-key map being applied for each path, and cleanup annotation coverage. Tests should cover active and snapshot purges, subdir/file movement, deleted-dir marker removal, bucket updates, and snapshot info persistence.
