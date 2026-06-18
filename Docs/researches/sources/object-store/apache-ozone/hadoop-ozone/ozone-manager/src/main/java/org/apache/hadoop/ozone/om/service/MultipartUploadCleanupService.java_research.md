<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/MultipartUploadCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/MultipartUploadCleanupService.java

Purpose: Background service that finds expired incomplete multipart uploads and submits OM requests to abort them.

Important APIs/types/functions: Extends `BackgroundService`. Constructor reads `OZONE_OM_MPU_EXPIRE_THRESHOLD` and `OZONE_OM_MPU_PARTS_CLEANUP_LIMIT_PER_TASK`, stores OM/key manager, creates a random client ID, and initializes counters. Important methods are `getRunCount`, `suspend`, `resume`, `getSubmittedMpuInfoCount`, `getTasks`, and nested `MultipartUploadCleanupTask`.

Control flow and persistence: The task runs only when not suspended and OM leader-ready. It calls `keyManager.getExpiredMultipartUploads(expireThreshold, mpuPartsLimitPerTask)`, counts expired MPUs, builds `MultipartUploadsExpiredAbortRequest` with bucket-grouped expired upload data, wraps it in an OM request of type `AbortExpiredMultiPartUploads`, and submits it through `OzoneManagerRatisUtils`. It increments submitted count after submission attempt; actual metadata deletion is handled by the abort request/response path.

Dependencies and integration: Depends on `KeyManager` MPU scanning, OM config keys, Ratis submission, and S3 multipart abort-expired request handling.

Risks and test signals: Expired uploads may be completed or aborted between scan and request processing, so downstream handling must be idempotent. Tests should cover leader gating, suspension, threshold filtering, per-task part limit, grouped request construction, submission failure retry behavior, and submitted count metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/MultipartUploadCleanupService.java -->
