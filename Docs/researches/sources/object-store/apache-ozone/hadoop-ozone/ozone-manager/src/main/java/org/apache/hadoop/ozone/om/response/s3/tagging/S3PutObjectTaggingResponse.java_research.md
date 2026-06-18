<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponse.java

Purpose: Persists updated S3 object tag metadata for non-FSO key-table layouts.

Important APIs/types/functions: Extends `OmKeyResponse`. The success constructor stores updated `OmKeyInfo`; the failure constructor stores layout and calls `checkStatusNotOK()`. `addToDBBatch` writes the complete `OmKeyInfo` back to the layout-specific key table under `getOzoneKey`.

Control flow and persistence: The response has no tag parsing logic. It assumes the request path has already validated and updated tags in `OmKeyInfo`, then performs a single batched key-table put. Cleanup metadata names `KEY_TABLE`.

Dependencies and integration: Integrated by S3 put-object-tagging requests. Depends on `BucketLayout`, `OMMetadataManager`, and `BatchOperation`.

Risks and test signals: The whole key record is rewritten, so tests should check preservation of existing object metadata while tags change. Include invalid-request failure no-op, overwrite of existing tags, and non-FSO layout table selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3PutObjectTaggingResponse.java -->
