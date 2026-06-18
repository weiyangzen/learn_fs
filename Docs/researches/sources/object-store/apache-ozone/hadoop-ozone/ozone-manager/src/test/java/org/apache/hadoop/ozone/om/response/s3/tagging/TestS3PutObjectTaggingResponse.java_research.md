# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponse.java

Purpose: Tests putting S3 object tags for legacy/default layout.

Important APIs/types/functions: Uses `S3PutObjectTaggingResponse`, `PutObjectTaggingResponse`, `OmKeyInfo.toBuilder().setTags`, key table, and `OMRequestTestUtils.addKeyToTable`.

Control flow: The test inserts an untagged key, verifies zero tags, creates a two-entry tag map, builds a modified key info with those tags, commits the put-tagging response, and verifies the persisted key has the expected tag count and is a distinct object instance.

State/persistence: Updates the committed key-table row with a non-empty tags map.

Dependencies/integration: Uses base key response fixture and RATIS/ONE key creation helper.

Risks/test signals: Does not verify exact tag values after persistence, only size. Does not test error status.
