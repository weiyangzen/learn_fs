<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/multipart_encryption_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/multipart_encryption_test.rs

Purpose: this module provides stepwise local-KMS tests for multipart encryption, starting with simple single-object encryption, then unencrypted multipart baseline, SSE-S3 multipart, large streaming-style SSE-S3 multipart, and SSE-KMS/SSE-C multipart modes.

Important APIs, types, and functions: it uses `LocalKMSTestEnvironment`, `sse_customer_key_md5_base64()`, `TEST_BUCKET`, AWS SDK multipart builders, `ServerSideEncryption`, and local `EncryptionType` enum with `SSEKMS` and `SSEC`. `test_multipart_encryption_type()` is the shared helper for SSE-KMS and SSE-C multipart uploads.

Control flow: each step starts local KMS and a bucket. Step 1 writes a small SSE-S3 object and verifies PUT/GET headers and bytes. Step 2 performs a two-part unencrypted upload as a baseline. Step 3 creates a two-part SSE-S3 upload, optionally validates create response SSE header, checks HEAD metadata, downloads, and compares data. Step 4 uploads three 6 MiB SSE-S3 parts to cross encryption chunk boundaries, then validates every byte. Step 5 uses the helper to test two-part SSE-KMS and SSE-C multipart uploads; SSE-C adds customer headers on create, every part, and GET.

State and persistence: state includes local KMS key files, temporary bucket data, multipart upload IDs, part ETags, encryption headers, and deterministic byte patterns. Buckets are deleted after successful steps.

Dependencies and integration points: depends on local KMS, RustFS multipart upload state, AWS SDK S3 streaming bodies, SSE-S3/SSE-KMS/SSE-C metadata propagation, and serial execution over `TEST_BUCKET`.

Risks: many tests duplicate coverage from `common.rs` and `kms_local_test.rs`, increasing runtime. Fixed initialization sleep can be flaky. Step 5 covers only SSE-KMS and SSE-C because SSE-S3 is covered in earlier steps. The code includes non-ASCII log icons, and large byte-by-byte validation can be slow.

Test signals: passing tests show baseline multipart works, SSE-S3 metadata and decryption work for normal and larger multi-part objects, encryption chunk boundaries do not corrupt data, SSE-KMS multipart returns `AwsKms`, and SSE-C multipart requires and accepts customer headers across all phases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/multipart_encryption_test.rs -->
