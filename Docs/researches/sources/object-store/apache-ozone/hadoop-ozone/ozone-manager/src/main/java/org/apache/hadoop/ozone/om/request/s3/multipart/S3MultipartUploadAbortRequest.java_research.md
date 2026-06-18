## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequest.java

Purpose: `S3MultipartUploadAbortRequest` aborts a specific multipart upload in non-FSO and base-layout-aware paths. It validates the request, deletes the multipart open key and multipart-info row from cache, releases quota for uploaded parts, and returns an abort response.

Important APIs/types/functions: `preExecute` normalizes the key, sets modification time, checks WRITE ACL, and user info. `validateAndUpdateCache` uses `getMultipartOpenKey`, `getBucketInfo`, `OmMultipartKeyInfo`, `QuotaUtil.getReplicatedSize`, open-key table, multipart-info table, and `S3MultipartUploadAbortResponse`. Validators cover EC finalization and old-client layout compatibility.

Control flow: Under the bucket lock, the request validates volume/bucket, computes the multipart-info DB key, resolves the multipart open key, fetches the open key and bucket info, warns if the open key is missing, fetches multipart info, fails with `NO_SUCH_MULTIPART_UPLOAD_ERROR` if multipart info is absent, updates the multipart info update ID, computes quota released from all parts, decrements bucket used bytes, tombstones the open-key row and multipart-info row, and constructs a success response.

State and persistence behavior: The open-key and multipart-info tables are invalidated through cache tombstones. Bucket used bytes are decremented in the copied bucket info included in the response. Delete-table updates are not required for validation and are handled by response processing.

Dependencies and integration points: It integrates with `OMMultipartUploadUtils`, OM bucket locks, quota accounting, S3 audit, metrics, cleanup of old orphan state, EC layout-feature gating, and bucket-layout validators.

Risks and edge cases: Open key absence is tolerated because legacy cleanup may leave orphan multipart info, but multipart-info absence is a client-visible no-such-upload failure. Quota release must use the multipart replication config. The method always tombstones the open key even if the earlier table get returned null.

Test signals: Cover normal abort, missing open key with existing multipart info, missing multipart info, quota release, metrics, audit upload ID, EC finalization rejection, old-client layout validation, and response replay.
