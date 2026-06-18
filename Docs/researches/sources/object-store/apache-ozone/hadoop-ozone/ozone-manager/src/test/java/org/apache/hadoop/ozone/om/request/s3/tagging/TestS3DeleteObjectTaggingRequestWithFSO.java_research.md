# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequestWithFSO.java

Purpose: adapts delete-object-tagging tests to FSO buckets. It inherits default delete-tagging tests and overrides key insertion, bucket layout, and request class.

Important APIs and types: `S3DeleteObjectTaggingRequestWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and `RatisReplicationConfig`.

Control flow: `addKeyToTable` changes the test `keyName` to `c/d/e/file1`, creates parent directories, builds an `OmKeyInfo` for leaf file name `file1` with parent/object IDs and tags, writes it to the FSO key table, and returns the FSO path key. Inherited tests then delete tags and assert state.

State and persistence behavior: the key table entry is addressed by volume ID, bucket ID, parent object ID, and file name. The request should clear tags for the FSO file row while preserving file identity and parent relationship.

Dependencies and integration points: the subclass uses the FSO production request class and returns FSO bucket layout, so inherited missing-volume/bucket/key tests exercise FSO validation path.

Risks covered: full path versus file-name mismatch, wrong parent ID lookup, and delete-tagging support divergence between default and FSO layouts.

Test signals: inherited success and error status assertions pass; after success the FSO key row exists and has zero tags.
