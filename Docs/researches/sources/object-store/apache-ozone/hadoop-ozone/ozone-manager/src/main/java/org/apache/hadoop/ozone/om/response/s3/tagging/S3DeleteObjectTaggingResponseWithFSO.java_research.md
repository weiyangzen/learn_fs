<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponseWithFSO.java

Purpose: FSO-specific response for deleting S3 object tags by updating the file-table entry addressed by object IDs.

Important APIs/types/functions: Extends `S3DeleteObjectTaggingResponse`. The success constructor adds `volumeId` and `bucketId`; the failure constructor delegates to the base failure path. It overrides `addToDBBatch` and `getBucketLayout`.

Control flow and persistence: Builds the FSO DB key with `getOzonePathKey(volumeId, bucketId, parentObjectID, fileName)` and writes updated `OmKeyInfo` to `getKeyTable(FILE_SYSTEM_OPTIMIZED)`, which maps to the file table. Cleanup table metadata names `FILE_TABLE`.

Dependencies and integration: Used by delete-object-tagging requests for FSO buckets. It relies on `OmKeyInfo` carrying correct parent object ID and file name.

Risks and test signals: Incorrect object ID or file name would update the wrong file-table row. Tests should cover nested FSO objects, tag removal on files with shared names under different parents, layout override behavior, and failure response no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/S3DeleteObjectTaggingResponseWithFSO.java -->
