# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestMultipartUploadCleanupService.java

Purpose: Tests that `MultipartUploadCleanupService` finds expired incomplete multipart uploads and submits abort cleanup for both default and FSO bucket layouts. Important APIs and types include `MultipartUploadCleanupService`, `KeyManager.getExpiredMultipartUploads`, `ExpiredMultipartUploadsBucket`, `OmMultipartInfo`, `OpenKeySession`, `OMRequestTestUtils`, `BucketLayout`, and MPU config keys.

Control flow: Class setup creates an OM test manager with short cleanup interval, short expiration threshold, and high per-task part cleanup limit. The parameterized test suspends the service, records counters, creates incomplete MPU keys in default and/or FSO buckets, optionally commits random parts, waits past expiration, verifies expired uploads are visible, resumes the service, and waits until no expired uploads remain.

State and persistence behavior: Test data persists volume/bucket rows, multipart info rows, open MPU part keys, and committed MPU part metadata. Cleanup changes OM metadata through normal abort/cleanup service paths and increments submitted MPU counters.

Dependencies and integration points: MPU initiate/open/commit part APIs, bucket layout-specific metadata tables, expiration scanning, service scheduling, and OM write client behavior. Risks include random distribution of volumes/buckets/part counts and short sleep-based expiration. Test signals are non-empty then empty expired-upload lists, increased service run count, and submitted MPU count at least equal to created uploads.
