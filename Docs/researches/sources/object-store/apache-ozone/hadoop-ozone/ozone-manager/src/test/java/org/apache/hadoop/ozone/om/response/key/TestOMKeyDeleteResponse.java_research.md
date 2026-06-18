# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponse.java

Purpose: Tests `OMKeyDeleteResponse` for object-store layout deletion behavior.

Important APIs/types/functions: Uses `OMKeyDeleteResponse`, `BucketLayout.OBJECT_STORE`, `OMRequestTestUtils.addKeyToTable`, `OmKeyLocationInfo`, `Pipeline`, `BlockID`, `RepeatedOmKeyInfo`, `deletedTable`, and `isDeletedKeyCommitted`.

Control flow: One test deletes a key with no blocks, verifying removal from key table and no deleted-table entry. Another appends a block to key info before deletion and verifies key removal plus deleted-table insertion with committed-delete flag. Error response test uses KEY_NOT_FOUND and verifies the key remains.

State/persistence: Successful delete removes from `keyTable(OBJECT_STORE)`. Keys with blocks are moved into `deletedTable` for asynchronous block cleanup; blockless keys are simply dropped. Error responses leave key table intact.

Dependencies/integration: Exercises storage-cleanup side effects via real metadata tables and HDDS pipeline/block helper objects.

Risks/test signals: Uses synthetic block/pipeline values. Range lookup verifies at least one deleted row but not exact key count. Bucket layout override means this test is specifically object-store, not default.
