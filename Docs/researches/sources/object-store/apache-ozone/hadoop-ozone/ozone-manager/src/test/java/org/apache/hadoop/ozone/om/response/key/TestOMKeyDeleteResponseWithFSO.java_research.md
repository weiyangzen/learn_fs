# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponseWithFSO.java

Purpose: FSO specialization of key-delete response tests.

Important APIs/types/functions: Uses `OMKeyDeleteResponseWithFSO`, `OMRequestTestUtils.addVolumeAndBucketToDB`, `addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: Overrides response construction to pass key name, key info, bucket info, recursive flag false, and volume ID. Overrides setup of the target key by creating volume/bucket entries, creating parent directories, building an FSO key with object/parent IDs, writing it to the file table, and returning the FSO DB key.

State/persistence: Inherited success tests remove rows from FSO key table and, for non-empty blocks, add delete-table entries. Error responses remain no-op.

Dependencies/integration: Uses FSO path ID helpers and request-test utilities for directory/file table setup.

Risks/test signals: The returned key path and response key info can be built from separately created objects, so the test is centered on table mutation rather than request validation.
