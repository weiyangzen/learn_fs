# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/S3ExpiredMultipartUploadsAbortResponse.java

Purpose: `S3ExpiredMultipartUploadsAbortResponse` persists aborting multiple expired multipart uploads grouped by bucket.

Important APIs and types: It extends `AbstractS3MultipartAbortResponse`, stores `Map<OmBucketInfo, List<OmMultipartAbortInfo>>`, and cleans open-key, open-file, deleted, multipart info, and bucket tables.

Control flow: `addToDBBatch` iterates each bucket entry and delegates to the shared abort helper for the list of MPUs.

State and persistence behavior: It removes multiple MPU open rows and multipart info rows, queues all parts in deleted table, and updates each bucket's used bytes.

Dependencies and integration points: It integrates expired MPU cleanup service, bucket layout data carried in `OmMultipartAbortInfo`, and shared abort response behavior.

Risks and test signals: Tests should cover multiple buckets, mixed bucket layouts, bucket update per group, failed response no-op, and deleted-table entries for every part.
