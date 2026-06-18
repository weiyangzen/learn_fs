<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_edge_cases_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_edge_cases_test.rs

Purpose: this module exercises KMS encryption boundary conditions and security checks: zero-byte and single-byte objects, exact 5 MiB multipart part size, invalid SSE-C inputs, concurrent encrypted uploads, and customer-key isolation.

Important APIs, types, and functions: uses `LocalKMSTestEnvironment`, `sse_customer_key_md5_base64()`, `ServerSideEncryption`, base64 encoding, `md5::compute`, `Arc`, `Semaphore`, tokio spawned tasks, and direct AWS SDK S3 calls.

Control flow: zero-byte and single-byte tests upload/download with SSE-S3/SSE-KMS/SSE-C and assert headers/body length. The multipart boundary test creates an SSE-S3 multipart upload, uploads one exact 5 MiB part, completes it, and verifies bytes. Invalid-key testing rejects a short SSE-C key, mismatched MD5, and GET of an SSE-C object without the key. Concurrent encryption spawns five uploads alternating SSE-S3, SSE-KMS, and SSE-C, requiring most to succeed. Key validation uploads the same plaintext under two SSE-C keys, verifies both decrypt with their own key, and rejects a cross-key read.

State and persistence: state includes temporary local KMS key files, bucket objects, multipart upload state, generated SSE-C keys/MD5 values, and concurrent task outcomes. Buckets are deleted after successful tests.

Dependencies and integration points: depends on AWS SDK SSE-C header behavior, RustFS SSE-C validation, local KMS availability, multipart minimum-size enforcement, tokio concurrency, and error mapping for bad encryption requests.

Risks: the invalid short-key MD5 uses hex MD5 rather than base64, so that assertion may fail for multiple reasons. The concurrent test permits one failure, reducing strictness. Fixed sleeps gate KMS readiness. Tests check error existence more often than precise S3 error code.

Test signals: passing tests indicate small/empty encrypted object handling works, exact minimum multipart part encryption succeeds, invalid SSE-C inputs are rejected, SSE-C keys are required for reads, concurrent mixed encryption is mostly stable, and wrong customer keys cannot decrypt data.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_edge_cases_test.rs -->
