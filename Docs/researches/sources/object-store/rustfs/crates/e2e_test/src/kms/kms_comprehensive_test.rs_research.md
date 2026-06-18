<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_comprehensive_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_comprehensive_test.rs

Purpose: this module composes broad KMS workflows over the local KMS backend: all single-object encryption modes, key management APIs, multipart encryption modes, mixed workloads, stress-size multipart uploads, key isolation, concurrent operations, and a simple performance benchmark.

Important APIs, types, and functions: it imports common helpers `test_sse_s3_encryption()`, `test_sse_kms_encryption()`, `test_sse_c_encryption()`, `test_kms_key_management()`, `test_all_multipart_encryption_types()`, `test_multipart_upload_with_config()`, `MultipartTestConfig`, `EncryptionType`, `create_sse_c_config()`, and `sse_customer_key_md5_base64()`. Local setup uses `LocalKMSTestEnvironment`.

Control flow: each `#[tokio::test]` starts local KMS, sleeps for initialization, creates `TEST_BUCKET`, and runs a scenario. The full workflow runs single-object helpers, admin key management, all multipart modes, and mixed multipart sizes/modes. Stress uploads 60 MiB-class objects for SSE-S3/SSE-KMS/SSE-C. Key isolation uploads with distinct SSE-C keys and verifies a wrong key fails. Concurrent operations spawn multiple multipart encrypted uploads with cloned S3 clients. The performance benchmark times representative small/medium/large SSE-S3 multipart uploads and logs throughput.

State and persistence: state is temporary local KMS key material, bucket/object data, multipart uploads and ETags, SSE-C customer keys, spawned tasks, and timing measurements. Tests delete the bucket after success, but failures rely on environment teardown.

Dependencies and integration points: depends heavily on the shared KMS common module, AWS SDK S3, tokio task scheduling, KMS admin endpoints, local KMS backend, and RustFS multipart encryption/decryption paths.

Risks: these tests are expensive and serial, and fixed sleeps can cause flakiness. Performance benchmark logs throughput but has no threshold, so it is informational rather than a regression gate. Concurrent tests run under `serial` at the test level but perform internal parallel uploads, stressing shared local KMS state. Large allocations may be memory-heavy.

Test signals: useful signals are end-to-end success across all encryption types, key API success, byte-exact multipart downloads for mixed sizes, wrong-key rejection, successful concurrent encrypted uploads, and no panics under larger object sizes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_comprehensive_test.rs -->
