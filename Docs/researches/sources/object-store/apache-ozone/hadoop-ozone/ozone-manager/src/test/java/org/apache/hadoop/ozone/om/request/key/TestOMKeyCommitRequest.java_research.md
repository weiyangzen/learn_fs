## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequest.java

**Purpose:** Tests `OMKeyCommitRequest` for object-store buckets, covering preExecute timestamping, open-key to committed-key transitions, block list reconciliation, hsync semantics, atomic rewrite/create-if-absent conflicts, quota errors, missing volume/bucket/key errors, overwrite deletion bookkeeping, and empty-file preallocated block handling.

**Important APIs/types/functions:** Uses `CommitKeyRequest`, `KeyArgs`, `KeyLocation`, `OMKeyCommitRequest`, `OMKeyCommitResponse`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `RepeatedOmKeyInfo`, metadata table accessors, and `BatchOperation`. Helpers include `createCommitKeyRequest`, `getKeyLocation`, `doPreExecute`, `addKeyToOpenKeyTable`, `getOzonePathKey`, and `verifyKeyName`.

**Control flow:** Tests create commit protobufs with client IDs and block lists, pre-execute to set modification time, seed volume/bucket and matching open-key rows, then validate/update cache. Success cases remove non-hsync open keys, write committed key table entries, and compare committed block locations. Failure cases omit volume/bucket/open key or set quota/atomic preconditions and assert error statuses.

**State and persistence behavior:** The file verifies `openKeyTable`, `keyTable`, `deletedTable`, and `bucketTable` mutations. Hsync commits keep open-key state while also updating committed state and increment bucket usage by newly synced blocks. Final commits remove open state. Overwrites generate deleted-table entries for replaced keys and uncommitted pseudo keys, then flush response batches to assert unique deleted keys.

**Dependencies and integration points:** Depends on shared SCM block mocks, Ozone config flags `OZONE_HBASE_ENHANCEMENTS_ALLOWED` and `OZONE_FS_HSYNC_ENABLED`, transaction/object ID generation via `ozoneManager.getObjectIdFromTxId`, and `OMRequestTestUtils` for table seeding. It integrates with deleted-block cleanup through `OMKeyCommitResponse.getKeysToDelete`.

**Risks:** Critical risks include data loss from deleting hsync blocks too early, incorrect atomic write conflict detection, quota counters changing on failed commits, stale open-key rows after final commit, misidentified uncommitted blocks, and deleted-table key collisions during overwrite cleanup.

**Test signals:** Strong assertions cover OK/error statuses, open-key deletion or retention, committed block list equality, modification time propagation, generation changes, expected-data-generation clearing, ACL preservation, bucket used bytes, deleted entry counts, and batch-persisted deleted-table rows.
