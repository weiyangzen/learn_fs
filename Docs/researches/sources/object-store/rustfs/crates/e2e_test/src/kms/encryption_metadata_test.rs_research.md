<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/encryption_metadata_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/encryption_metadata_test.rs

Purpose: this module validates externally visible metadata and physical storage behavior for managed encryption. It ensures SSE-S3/SSE-KMS headers appear on HEAD/GET, internal RustFS encryption metadata is not exposed as user metadata, copies preserve encryption, multipart encrypted uploads decrypt correctly, and plaintext is not visible in stored files.

Important APIs, types, and functions: `assert_managed_encryption_metadata_hidden()` checks user metadata for hidden internal keys such as `x-rustfs-encryption-key` and IV/context fields. `assert_storage_encrypted()` walks the storage root with a `VecDeque`, reads candidate files whose paths contain bucket/key fragments, and fails if plaintext bytes appear. Tests use `LocalKMSTestEnvironment`, bucket encryption builders, `ByteStream`, multipart builders, `copy_object`, `head_object`, and `get_object`.

Control flow: the SSE-S3 test sets bucket default AES256, uploads without explicit encryption, heads the object, checks the SSE header, hides internal metadata, and scans disk. The SSE-KMS/copy test sets bucket default KMS key, uploads, heads source, copies to a new key, heads destination, downloads the copy, and scans both source and destination storage. The multipart test configures SSE-KMS default encryption, uploads two 5 MiB patterned parts, completes the upload, checks HEAD metadata, downloads combined bytes, and scans storage for plaintext.

State and persistence: state includes local KMS keys, bucket encryption config, object metadata, copied-object metadata, multipart metadata, and files under the temporary RustFS storage root. The disk scanner observes implementation storage files directly.

Dependencies and integration points: depends on local KMS, AWS SDK S3 encryption headers, RustFS copy semantics, metadata projection, multipart encryption persistence, and the on-disk object layout.

Risks: scanning for plaintext is heuristic and path-filtered; compressed, chunked, or differently named storage could evade or falsely fail the scan. It couples tests to temp-dir storage internals. Fixed sleeps for KMS readiness can be flaky. It does not validate exact internal metadata contents, only that selected keys are absent from user metadata.

Test signals: passing tests show managed encryption metadata remains internal, HEAD reports expected SSE mode/key ID, copy preserves SSE-KMS configuration and payload, multipart encrypted data decrypts correctly, and plaintext bytes are not found in relevant stored files.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/encryption_metadata_test.rs -->
