# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3ExpiredMultipartUploadsAbortRequest.java

Purpose: tests `S3ExpiredMultipartUploadsAbortRequest`, the background cleanup request that aborts expired multipart uploads. It is parameterized over DEFAULT and FSO bucket layouts and extends `TestS3MultipartRequest` for OM/multipart helper setup.

Important APIs and types: `S3ExpiredMultipartUploadsAbortRequest`, `MultipartUploadsExpiredAbortRequest`, `ExpiredMultipartUploadsBucket`, `ExpiredMultipartUploadInfo`, `OmMultipartKeyInfo`, `OmMultipartUpload`, `OMMultipartUploadUtils`, `OMMetrics`, `UniqueId`, `BucketLayout`, and multipart initiate/commit request classes. Helpers create real MPU rows with committed parts, create non-existent mock MPU keys, and remove related open keys to simulate orphan state.

Control flow: tests create volumes/buckets, generate MPUs via initiate followed by per-part commits, build an expired-abort request from DB keys, call `preExecute`, and then run `validateAndUpdateCache`. Covered scenarios include missing MPU rows, subset deletion across volume/bucket combinations, update-ID filtering, orphan MPUs whose open keys were already cleaned, and metric accounting.

State and persistence behavior: successful abort removes entries from `multipartInfoTable` and the corresponding MPU open key from the layout-specific open-key table. In FSO, open keys are derived from volume ID, bucket ID, parent ID, file name, and upload ID; `multipartInfoTable` still uses the logical multipart key. The cleanup tolerates absent rows and orphaned open-key rows. Update IDs newer than the request transaction are retained.

Dependencies and integration points: integrates with production multipart initiate and commit request paths to seed realistic multipart state. It uses `OMMultipartUploadUtils.getMultipartOpenKey` to map multipart DB keys back to open-key table rows. The tests model the MPU cleanup service and older orphan conditions referenced around HDDS-9098.

Risks covered: cleanup must be idempotent, must not delete newer transaction data, must not fail on orphaned state, and must correctly count parts aborted. FSO path mapping is high risk because multipart table keys and open-file keys differ.

Test signals: `Status.OK`, expected existence/non-existence in `multipartInfoTable` and open-key table, metric counters for requests/submitted/aborted/parts/failures, and retention of higher-update-ID MPU rows.
