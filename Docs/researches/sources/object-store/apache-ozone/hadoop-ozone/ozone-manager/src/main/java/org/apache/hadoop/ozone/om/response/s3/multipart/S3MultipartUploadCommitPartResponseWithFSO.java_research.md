<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponseWithFSO.java

Purpose: FSO-specialized response for committing one S3 multipart upload part. It inherits all mutation behavior from `S3MultipartUploadCommitPartResponse` and exists to bind the response to the file-system-optimized bucket layout and the correct cleanup table metadata.

Important APIs/types/functions: The only public API is the constructor accepting `OMResponse`, multipart DB key, open key, optional `OmMultipartKeyInfo`, optional delete map, optional open part key, `OmBucketInfo`, bucket object ID, and `BucketLayout`. `@CleanupTableInfo` names `OPEN_FILE_TABLE`, `DELETED_TABLE`, `MULTIPART_INFO_TABLE`, and `BUCKET_TABLE`.

Control flow and persistence: Construction passes all request-derived state to the superclass. Runtime DB updates are therefore the superclass flow: update multipart metadata with the committed part, delete the FSO open-file entry, move replaced or pseudo part key versions to the deleted table, and update bucket accounting when supplied.

Dependencies and integration: Integrated by S3 multipart commit-part requests for FSO buckets. It depends on OM helper models (`OmMultipartKeyInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmBucketInfo`) and on the superclass implementation for actual batch writes.

Risks and test signals: The risk is constructor parameter mismatch because the class itself adds no validation. Tests should cover FSO commit-part replacing an existing part, deleting the open-file row, preserving multipart info, and updating deleted table and bucket usage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3MultipartUploadCommitPartResponseWithFSO.java -->
