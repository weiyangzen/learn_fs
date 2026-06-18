## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequestWithFSO.java

**Purpose:** Runs the base commit test suite under FSO layout by adapting open-key insertion, path keys, and key-name expectations to FSO's parent-object-ID addressing.

**Important APIs/types/functions:** Overrides `getOzonePathKey`, `addKeyToOpenKeyTable`, `getOmKeyCommitRequest`, `getBucketLayout`, and `verifyKeyName`. Uses `OMKeyCommitRequestWithFSO`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, `OMMetadataManager.getOzonePathKey`, `OzoneFSUtils.getFileName`, and FSO `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

**Control flow:** When a parent directory is present, the helper creates FSO directory rows and records `parentID`; otherwise it uses the bucket object ID as parent. It builds `OmKeyInfo` with parent object ID, appends allocated blocks, and inserts it into the FSO open file table before inherited commit tests run.

**State and persistence behavior:** FSO state uses volume ID, bucket object ID, parent object ID, and leaf file name for DB keys. The class ensures inherited assertions read from the same open/closed tables but with FSO key names. It also verifies committed `OmKeyInfo.keyName` stores only the leaf file name under prefix layout.

**Dependencies and integration points:** Integrates base commit behavior with `OMKeyCommitRequestWithFSO` and FSO file-table helpers. It depends on bucket object IDs being available after volume/bucket setup and on parent directory creation for nested key tests.

**Risks:** The main risks are parent ID not initialized before open-file insertion, full path vs leaf name confusion, bucket-not-found paths using sentinel IDs, and inherited object-store overwrite/hsync assertions missing FSO-specific identity bugs.

**Test signals:** Passing inherited commit, overwrite, hsync, quota, and missing-state tests plus FSO-specific `verifyKeyName` confirms FSO commit resolves and persists files with the expected DB identity.
