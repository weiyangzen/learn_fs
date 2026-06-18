<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_local_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_local_test.rs

Purpose: this file provides local-backend KMS E2E tests for admin status/key APIs, SSE-C key isolation, SSE-S3 large object upload, and multipart uploads under SSE-S3/SSE-KMS/SSE-C.

Important APIs, types, and functions: tests use `LocalKMSTestEnvironment`, `get_kms_status()`, `skip_if_kms_admin_tool_unavailable()`, `test_kms_key_management()`, `test_sse_c_encryption()`, `sse_customer_key_md5_base64()`, and local helper functions `test_multipart_upload_with_sse_s3()`, `test_multipart_upload_with_sse_kms()`, `test_multipart_upload_with_sse_c()`, and disabled `test_large_multipart_upload()`.

Control flow: `test_local_kms_end_to_end()` starts local KMS, checks KMS status, creates a bucket, runs key management and SSE-C only, then exits after a debugging-era early path with SSE-S3/SSE-KMS/error scenarios commented out. Key isolation uploads two SSE-C objects with different keys and verifies wrong-key access fails. Large-file test uploads/downloads a 1 MiB SSE-S3 object. Multipart test runs 2-part 5 MiB uploads for SSE-S3, SSE-KMS, and SSE-C, verifying headers and byte equality; the larger 30 MiB streaming helper remains dead code.

State and persistence: state includes local key files, KMS status/configuration, bucket objects, SSE-C key material, multipart upload IDs/ETags, and object metadata. Successful tests delete `TEST_BUCKET`.

Dependencies and integration points: depends on local KMS startup flags, admin KMS API availability through `awscurl`, AWS SDK S3 encryption headers, multipart encryption/decryption, and common test environment cleanup.

Risks: the main end-to-end test is intentionally incomplete, with SSE-S3/SSE-KMS/error checks commented out. Several log messages include “CLAUDE TEST DEBUG”, indicating temporary diagnostics in committed tests. Large multipart streaming coverage is disabled. Some tests use panic-style `expect()` instead of returning structured errors.

Test signals: current passing signals cover local KMS startup/status, key management, SSE-C single-object encryption, customer-key isolation, 1 MiB SSE-S3 object integrity, and two-part multipart encryption for SSE-S3/SSE-KMS/SSE-C. They do not fully signal local KMS SSE-S3/SSE-KMS single-object behavior from the nominal end-to-end test.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_local_test.rs -->
