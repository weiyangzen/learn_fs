# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tagging/TestS3PutObjectTaggingRequest.java

Purpose: tests default-layout `S3PutObjectTaggingRequest`, which replaces object tags on an existing key. It covers pre-execute stability, success, empty tag set, and not-found errors.

Important APIs and types: `S3PutObjectTaggingRequest`, protobuf `PutObjectTaggingRequest`, `KeyArgs`, `KeyValueUtil`, `OMResponse`, `Type.PutObjectTagging`, `OmKeyInfo`, `RatisReplicationConfig`, and `OMRequestTestUtils`.

Control flow: success creates volume/bucket, inserts an untagged key, builds a put-tagging request with random tags, pre-executes, validates, and reads the key table. The empty-tag test sends an empty tag map and expects success with an empty stored tag set. Negative tests cover absent volume, bucket, and key.

State and persistence behavior: success updates the key-table cache entry's tag map to exactly match request tags while preserving volume, bucket, and key name. Pre-execute must not set modification time for object tagging and must not alter key args. Empty tag input is a valid replacement, not a validation failure.

Dependencies and integration points: extends `TestOMKeyRequest` and uses `KeyValueUtil.toProtobuf` when building request tags. The FSO subclass reuses most tests by overriding table insertion and request class.

Risks covered: accidental mtime mutation, partial tag merge instead of replacement, rejecting empty tag sets, updating state on not-found paths, and losing key identity fields.

Test signals: `PutObjectTaggingResponse` present, status `OK`, command type `PutObjectTagging`, exact tag key/value matches, empty tag success, and statuses `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `KEY_NOT_FOUND`.
