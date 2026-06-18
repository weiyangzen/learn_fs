<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponse.java

Purpose: Persists an object key after S3 object tags have been removed in non-FSO layouts.

Important APIs/types/functions: Extends `OmKeyResponse`. The success constructor accepts `OMResponse` and updated `OmKeyInfo`; the failure constructor accepts `BucketLayout` and calls `checkStatusNotOK()`. `addToDBBatch` writes the supplied key info to the layout-specific key table using `getOzoneKey`.

Control flow and persistence: The request layer mutates the tag metadata inside `OmKeyInfo`. The response batches a `putWithBatch` to `getKeyTable(getBucketLayout())` under `volume/bucket/key` DB key. Cleanup table metadata names `KEY_TABLE`.

Dependencies and integration: Used by S3 delete-object-tagging request handling. It depends on `OMMetadataManager`, `BatchOperation`, and key-table layout selection from `OmKeyResponse`.

Risks and test signals: The response overwrites the whole `OmKeyInfo`, so stale request-side fields can regress unrelated metadata. Tests should verify tag removal, retention of ACL/version/block fields, failure no-op behavior, and correct key table for non-FSO bucket layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponse.java -->
