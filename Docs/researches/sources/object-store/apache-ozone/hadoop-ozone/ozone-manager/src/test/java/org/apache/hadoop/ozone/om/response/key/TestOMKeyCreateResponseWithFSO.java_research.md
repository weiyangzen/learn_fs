# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponseWithFSO.java

Purpose: FSO specialization of key-create response tests.

Important APIs/types/functions: Uses `OMKeyCreateResponseWithFSO`, `getOpenFileName`, volume/bucket IDs, bucket object ID parentage, `RatisReplicationConfig`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: Overrides key info to set object ID, parent object ID, and update ID. Overrides open-key computation to use FSO numeric IDs, and response construction to pass an empty parent-dir list plus volume ID. Inherited tests verify write/no-op behavior.

State/persistence: Success creates an FSO open-file row; error response does not write.

Dependencies/integration: Reuses base key-create tests and OM metadata ID lookups.

Risks/test signals: Does not verify recursive directory creation or parent-dir list behavior because it passes an empty list. Focus is the FSO response write path.
