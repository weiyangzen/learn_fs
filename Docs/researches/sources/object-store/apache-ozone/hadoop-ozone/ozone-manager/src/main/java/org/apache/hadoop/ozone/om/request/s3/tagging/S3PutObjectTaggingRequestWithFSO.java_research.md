
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3PutObjectTaggingRequestWithFSO.java

Purpose: FSO-specific `PutObjectTagging` handler that updates tags on file entries in file-system-optimized buckets and rejects directory tagging.

Important APIs and types: Extends `S3PutObjectTaggingRequest`; uses `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OzoneFSUtils.getFileName`, `OMMetadataManager.getOzonePathKey`, `S3PutObjectTaggingResponseWithFSO`, and FSO volume/bucket object IDs.

Control flow: It uses the inherited `preExecute`. In validation it takes the bucket write lock, validates volume/bucket, resolves the file status, rejects missing keys and directories, computes the FSO path-table DB key from volume ID, bucket ID, parent object ID, and file name, updates tags and update ID, writes the key-table cache entry, and returns the FSO response containing the object IDs.

State and persistence behavior: Persists a replacement `OmKeyInfo` in the FSO key table cache. It sets the `OmKeyInfo` key name back to the leaf file name before computing the DB key and leaves object modification time unchanged.

Dependencies and integration points: Integrates tagging with FSO path lookup, bucket object identity, file table response flushing, OM metrics, and bucket-level locking. It shares request normalization and ACL behavior with the base tagging class.

Risks: Directory rejection is a behavior boundary that clients may hit when S3 paths overlap Ozone directories. The method logs all failures as errors, unlike the base class's selective logging. Tests should cover nested file paths, directory input, missing parent/key, and correct cache key construction.
