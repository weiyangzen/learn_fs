<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/bucket_default_encryption_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/bucket_default_encryption_test.rs

Purpose: this KMS E2E module verifies bucket default encryption behavior for SSE-S3 and SSE-KMS, including normal `PutObject`, multipart upload inheritance, explicit request overrides, and default KMS key population when a bucket encryption rule omits a key ID.

Important APIs, types, and functions: tests use `LocalKMSTestEnvironment`, `ServerSideEncryptionConfiguration`, `ServerSideEncryptionRule`, `ServerSideEncryptionByDefault`, `ServerSideEncryption`, S3 bucket encryption APIs, object APIs, multipart APIs, and `TEST_BUCKET`.

Control flow: each test starts RustFS with local KMS and a generated default key, sleeps briefly for initialization, creates the test bucket, installs a bucket encryption configuration, performs an object or multipart operation without explicit encryption where inheritance is expected, and validates response/get/head encryption metadata. The override test configures default SSE-S3 but uploads with explicit SSE-KMS and asserts the explicit key wins. The no-key-ID test writes an SSE-KMS rule with an empty key ID and verifies `GetBucketEncryption` returns the configured default key.

State and persistence: state includes local KMS key files, bucket encryption configuration, object encryption metadata, KMS key IDs, and multipart upload metadata. Cleanup mostly relies on temporary environment drop; explicit bucket deletion is not consistently called in this file.

Dependencies and integration points: depends on KMS startup flags from `LocalKMSTestEnvironment`, AWS SDK bucket-encryption model types, RustFS bucket encryption persistence, KMS default key resolution, object encryption pipeline, and multipart completion metadata propagation.

Risks: the fixed `TEST_BUCKET` and serial execution are required. Initialization uses fixed sleeps instead of readiness polling. One TODO notes explicit “no encryption” override is skipped. Some assertions use `unwrap()` for KMS key IDs, so missing headers produce panics rather than diagnostic errors.

Test signals: success means bucket defaults are applied to PUT and create-multipart paths, SSE-KMS key IDs survive PUT/GET and multipart completion, explicit SSE-KMS overrides bucket SSE-S3, and empty SSE-KMS bucket rules are normalized to the local default key.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/bucket_default_encryption_test.rs -->
