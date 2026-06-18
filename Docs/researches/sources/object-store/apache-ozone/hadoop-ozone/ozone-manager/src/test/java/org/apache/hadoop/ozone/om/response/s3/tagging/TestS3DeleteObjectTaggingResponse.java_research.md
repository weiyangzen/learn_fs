# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponse.java

Purpose: Tests deleting S3 object tags for legacy/default layout.

Important APIs/types/functions: Extends `TestOMKeyResponse`; uses `S3DeleteObjectTaggingResponse`, `DeleteObjectTaggingResponse`, `OmKeyInfo.toBuilder().setTags(Collections.emptyMap())`, key table, and `OMRequestTestUtils.addKeyToTable`.

Control flow: The test builds a successful delete-tagging response, inserts a key with two tags, reads and verifies the tags, builds an updated `OmKeyInfo` with empty tags, commits the response, and verifies the persisted key has zero tags and is a different object instance.

State/persistence: Replaces the key-table row with an `OmKeyInfo` whose tag map is empty.

Dependencies/integration: Uses base key fixture and RATIS/ONE key creation helpers.

Risks/test signals: Does not test error response/no-op behavior. It validates tag count, not exact removal timestamp or version behavior.
