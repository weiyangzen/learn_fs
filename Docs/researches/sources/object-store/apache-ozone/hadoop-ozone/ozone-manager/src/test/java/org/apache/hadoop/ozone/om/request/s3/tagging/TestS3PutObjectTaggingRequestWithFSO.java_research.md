# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequestWithFSO.java

Purpose: adapts put-object-tagging coverage to FSO layout and adds a directory-specific unsupported-operation test.

Important APIs and types: `S3PutObjectTaggingRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and `RatisReplicationConfig`.

Control flow: inherited tests use `addKeyToTable` to create `c/d/e/file1` in FSO key table with parent directories and leaf file name. `testValidateAndUpdateCachePutObjectTaggingToDir` creates the file/parents, then sends a put-tagging request against the parent directory path `c/d/e` and validates the response.

State and persistence behavior: file tagging updates the FSO key table row keyed by numeric parent identity. Directory tagging is rejected with `NOT_SUPPORTED_OPERATION`; the request must not treat a directory entry as a taggable object key.

Dependencies and integration points: returns the FSO request subclass and FSO bucket layout so default success and not-found tests run through FSO validation. Directory resolution depends on the parent rows created by `addParentsToDirTable`.

Risks covered: allowing tags on directories, resolving full path incorrectly, wrong file name in `OmKeyInfo`, and divergence in tag semantics between FSO and default layout.

Test signals: inherited put-tagging success/error assertions plus explicit `Status.NOT_SUPPORTED_OPERATION` when tagging a directory path.
