## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyPurgeRequestAndResponse.java

**Purpose:** Tests non-directory key purge request/response behavior for deleted keys and snapshot renamed entries in active and snapshot metadata databases.

**Important APIs/types/functions:** Uses `OMKeyPurgeRequest`, `OMKeyPurgeResponse`, `PurgeKeysRequest`, `DeletedKeys`, `PurgeKeysResponse`, `SnapshotInfo`, `OmSnapshot`, `TransactionInfo`, and `BatchOperation`. Helpers include `createAndDeleteKeysAndRenamedEntry`, `createPurgeKeysRequest`, and `preExecute`.

**Control flow:** Helpers create volume/bucket/key rows, add renamed-table entries, then delete keys into the deleted table. Tests build purge requests with deleted keys and renamed entries, optionally target a snapshot DB key, pre-execute, validate/update cache, construct a response, and manually call `addToDBBatch` followed by store commit.

**State and persistence behavior:** Active purge removes rows from `deletedTable` and `snapshotRenamedTable`. Snapshot purge validates that deleted/renamed rows are in the snapshot metadata manager rather than active DB, updates `SnapshotInfo.lastTransactionInfo`, acquires snapshot DB content read lock during batch application, and removes rows from snapshot tables after commit.

**Dependencies and integration points:** Depends on snapshot creation from `TestOMKeyRequest`, `OMRequestTestUtils.deleteKey` and `addRenamedEntryToTable`, snapshot manager lookup, lock spying for `SNAPSHOT_DB_CONTENT_LOCK`, and asynchronous batch commits.

**Risks:** Risks include purging active DB instead of snapshot DB, failing to delete renamed entries with deleted keys, missing snapshot last-transaction updates, not acquiring snapshot DB locks, and response batch behavior diverging from validate/update cache state.

**Test signals:** Before/after existence checks in active or snapshot `deletedTable` and `snapshotRenamedTable`, snapshot transaction info equality, lock acquisition list equality, and successful batch commits provide the confidence signals.
