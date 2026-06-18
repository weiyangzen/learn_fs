<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/all_buckets_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/all_buckets_test.go

Purpose: integration-tests filesystem behavior when gcsfuse mounts all accessible buckets at the root rather than a single bucket.

Important APIs/types/functions: `AllBucketsTest`, `SetUpTestSuite`, `BaseDir_Ls`, `BaseDir_Write`, `BaseDir_Rename`, and `SingleBucket_ReadAfterWrite`.

Control flow: setup creates three fake buckets and sets `serverCfg.BucketName` to empty through the shared `fsTest` harness. Tests assert that base-directory listing and writes are unsupported or fail with I/O errors, that renaming buckets or moving files across buckets is unsupported, and that normal read/write/seek/write-at behavior works inside an individual bucket subdirectory.

State and persistence: uses in-memory fake buckets and a real FUSE mount point created by `fsTest`. File contents written through the mount are persisted to the fake bucket for the life of the test suite.

Dependencies and integration points: depends on fake storage, `gcs.Bucket`, `fuse` mounted filesystem, and the shared test harness in `fs_test.go`. It validates `makeRootForAllBuckets`, base directory inode behavior, and rename restrictions across bucket roots.

Risks: error assertions match substrings such as `operation not supported` and `input/output error`, which may differ across platforms or FUSE layers. The tests rely on a real mounted filesystem, so they require FUSE support in the environment.

Test signals: confirms multi-bucket root is not a normal writable/listable GCS directory, cross-bucket renames are blocked, and bucket-scoped file operations still behave like regular file operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/all_buckets_test.go -->
