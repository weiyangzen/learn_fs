# sources/object-store/rustfs/crates/e2e_test/src/quota_test.rs

## Purpose

This file implements RustFS bucket quota integration tests. It starts a RustFS test environment, uses S3 APIs for object operations, uses `awscurl` helpers for signed admin quota endpoints, and validates quota setting, clearing, usage accounting, operation checks, permissions, copy, batch delete, and multipart completion behavior.

## Important APIs, Types, And Functions

`skip_without_awscurl()` gates every integration test. If the external `awscurl` dependency is unavailable, tests log and return `Ok(())` rather than failing.

`QuotaTestEnv` groups `RustFSTestEnvironment`, an AWS SDK S3 `Client`, and a generated bucket name. `new()` starts a RustFS server and creates an S3 client. Methods wrap common operations: `create_bucket`, `cleanup_bucket`, `set_bucket_quota`, `get_bucket_quota`, `clear_bucket_quota`, `get_bucket_quota_stats`, `check_bucket_quota`, `upload_object`, `object_exists`, `get_bucket_usage`, bucket-specific quota/stats setters, and bucket-specific upload.

Admin quota calls use endpoints under `/rustfs/admin/v3/quota/<bucket>`, `/quota-stats/<bucket>`, and `/quota-check/<bucket>` with JSON bodies. Object operations use AWS SDK S3 calls such as `put_object`, `head_object`, `delete_object`, `delete_objects`, `copy_object`, multipart create/upload/complete, and bucket management through the common test environment.

## Control Flow

Each `#[tokio::test]` is serial. The typical flow initializes logging, skips if `awscurl` is unavailable, constructs `QuotaTestEnv`, creates one or more buckets, sets a hard quota, performs S3 operations, checks admin quota APIs, then cleans up buckets. Error-path tests intentionally expect failed S3 or admin calls.

The basic operations test sets a 1 MiB quota, uploads two 512 KiB objects, then expects an extra 1 KiB upload to fail and not create an object. Update/clear changes quota from 512 KiB to 2 MiB, clears it, and confirms large upload succeeds without a quota. Delete operations and batch delete verify freed quota permits later uploads. Usage/statistics tests assert exact current usage, remaining quota, and percentage fields. The quota-check test checks PUT and DELETE decision responses without necessarily performing the operation.

Multi-bucket tests assert quotas and usage are independent between buckets. Error-handling and HTTP endpoint tests cover invalid quota type `SOFT` and nonexistent bucket errors. The normal-user permissions test creates a user, attaches `readwrite`, confirms reads of quota and stats succeed, and confirms set/clear are denied. Copy and multipart tests validate quota enforcement for S3 copy and multipart complete paths.

## State And Persistence Behavior

Quota config is persisted in the RustFS test environment through admin APIs. Usage state is derived from actual S3 objects in buckets. Tests mutate buckets by uploading, deleting, copying, and completing multipart uploads, then query stats to ensure quota accounting reflects those changes. `cleanup_bucket` lists and deletes objects before deleting the bucket, but some multi-bucket cleanup paths delete buckets directly and assume test objects or bucket-delete semantics allow cleanup.

Multipart behavior is important: parts may upload successfully, but quota enforcement is expected at complete time for an over-quota object. The test verifies the completed object does not exist after a failed complete.

## Dependencies And Integration Points

The file depends on local `common` helpers including `RustFSTestEnvironment`, `awscurl_*`, `awscurl_available`, and logging. It uses `aws_sdk_s3::Client`, AWS SDK S3 types for copy, delete, and multipart, `serde_json`, `uuid`, `serial_test`, and `tracing`. It is not part of the protocol runner; it is a separate integration-test module for admin quota and S3 behavior.

## Risks And Edge Cases

The tests are skipped silently when `awscurl` is missing, so CI environments without that binary lose quota admin coverage. Several helper methods detect admin errors by checking whether the response string contains `"error"`, which may be brittle if successful payloads include that substring or error payload shapes change. `object_exists` falls back to string matching for 404/NotFound and then service-error inspection, which is pragmatic but broad.

Fixed exact usage assertions assume no compression, metadata overhead, or delayed accounting; they validate logical object byte counts. Multipart tests upload two 5 MiB parts after a 5 MiB existing object under a 10 MiB quota, expecting complete failure. If enforcement moves earlier to part upload, the test shape may need adjustment while preserving the quota property.

## Test Signals

Signals include exact quota values from GET, S3 upload success/failure, object existence after failed writes/copies/completes, exact usage and remaining quota stats, quota-check `allowed` and `remaining_quota` fields, independent per-bucket usage, admin error codes for invalid type and nonexistent bucket, normal-user read-versus-write permission boundaries, copy quota enforcement, batch-delete freeing quota, and multipart complete enforcement.
