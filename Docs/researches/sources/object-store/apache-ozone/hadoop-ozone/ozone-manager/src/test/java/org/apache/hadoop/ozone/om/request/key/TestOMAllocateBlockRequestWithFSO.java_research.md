# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequestWithFSO.java

FSO specialization of allocate-block tests. It overrides open-key seeding, request construction, bucket layout, and open-key verification to use object-id-qualified FSO paths.

`addKeyToOpenKeyTable` rewrites the inherited `keyName` into parent directory plus leaf file, seeds parent directories with `addParentsToDirTable`, builds an `OmKeyInfo` with object ID and parent object ID, and writes it to the open file table. `getOmAllocateBlockRequest` returns `OMAllocateBlockRequestWithFSO`; `getBucketLayout` returns `FILE_SYSTEM_OPTIMIZED`. `verifyPathInOpenKeyTable` traverses `directoryTable` with `StringUtils.split` and reads the open key table using `getOpenFileName(volumeId, bucketId, parentId, fileName, clientId)`.

State behavior uses FSO `directoryTable` parent chains and open file table keys rather than default open key names. Successful inherited validation appends the allocated block to the object-id-qualified open file row. Dependencies include FSO allocate request, `OmDirectoryInfo`, `OmKeyInfo`, path key APIs, `RatisReplicationConfig`, and inherited SCM/block assertions.

Risks are incorrect parent ID traversal, writing to default open key naming, and mutation of inherited `keyName` before verification. Signals are inherited allocate-block assertions plus non-null FSO directory/open-file lookups and matching appended block data.
