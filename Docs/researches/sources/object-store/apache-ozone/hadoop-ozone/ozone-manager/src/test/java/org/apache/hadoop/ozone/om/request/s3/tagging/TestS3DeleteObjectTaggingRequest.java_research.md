# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3DeleteObjectTaggingRequest.java

Purpose: tests default-layout `S3DeleteObjectTaggingRequest`, which removes all tags from an existing key without changing other key identity fields.

Important APIs and types: `S3DeleteObjectTaggingRequest`, protobuf `DeleteObjectTaggingRequest`, `KeyArgs`, `OMResponse`, `Type.DeleteObjectTagging`, `OmKeyInfo`, `RatisReplicationConfig`, and `OMRequestTestUtils`.

Control flow: pre-execute test builds a delete-tagging request and verifies the request retains volume, bucket, key, and tags list while not setting modification time. Success test creates volume/bucket, inserts a key with random tags, pre-executes, validates, and reads the key table. Negative tests cover missing volume, missing bucket, and missing key.

State and persistence behavior: success mutates the key-table cache entry so `OmKeyInfo.getTags()` becomes empty while volume, bucket, and key name remain unchanged. The request does not set modification time during pre-execute.

Dependencies and integration points: extends `TestOMKeyRequest` for common OM metadata fixture. Uses key-table lookup via `omMetadataManager.getOzoneKey` and supports bucket layout override by FSO subclass.

Risks covered: deleting the key instead of tags, changing modification time unexpectedly, writing tags on failed lookup, returning the wrong command type, or losing key identity fields.

Test signals: `DeleteObjectTaggingResponse` present, status `OK`, command type `DeleteObjectTagging`, empty tags after success, and statuses `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `KEY_NOT_FOUND` for failures.
