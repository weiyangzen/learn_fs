<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_fault_recovery_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_fault_recovery_test.rs

Purpose: this module tests local KMS resilience under key-directory/key-file faults, multipart interruption, and rapid request load. It focuses on graceful failure/recovery rather than exact failure modes when keys may be cached.

Important APIs, types, and functions: uses `LocalKMSTestEnvironment`, local filesystem `fs::rename`, `fs::copy`, `fs::write`, `fs::remove_file`, AWS SDK `ServerSideEncryption`, multipart create/upload/abort/complete APIs, tokio sleeps/spawns, and `TEST_BUCKET`.

Control flow: the directory-unavailable test uploads an encrypted object, renames the key directory away, attempts another upload expecting failure or cached success, restores the directory, uploads again, and verifies the original object remains readable. The corrupted-key test backs up the default key file, overwrites it with invalid bytes, attempts encrypted upload, restores the key, and verifies new uploads work. The multipart-interruption test uploads two encrypted parts, aborts the upload, asserts completion of the aborted upload fails, then starts and completes a new encrypted multipart upload with all parts. The resource-constraints test launches ten rapid SSE-S3 uploads and requires at least seven successes.

State and persistence: state includes local KMS key directory contents, backup key files, bucket objects, aborted multipart upload records, completed multipart object data, and task results. Fault tests mutate files under the temp KMS directory while RustFS is running.

Dependencies and integration points: depends on local KMS file-backed key loading/cache behavior, RustFS encryption paths, multipart abort semantics, and S3 object readability after KMS faults.

Risks: comments explicitly allow cached keys to make “failure” attempts succeed, so these are recovery smoke tests more than deterministic negative tests. Filesystem rename behavior may differ across platforms. Fixed waits may not match cache invalidation or watcher timing. Rapid upload threshold allows partial failure.

Test signals: useful signals are server responsiveness during key material faults, successful encrypted upload after restoration, original encrypted object readability, inability to complete aborted uploads, successful retry with a fresh upload ID, byte-exact final multipart data, and acceptable success rate under bursts.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_fault_recovery_test.rs -->
