# sources/object-store/rustfs/crates/ecstore/tests/minio_generated_read_test.rs

Purpose: feature-gated integration coverage for reading MinIO-generated encrypted multipart fixtures through RustFS. It is compiled only with `rio-v2` and ignored by default because it needs fixture data plus a local static KMS key.

Important APIs and flow: fixture discovery uses `RUSTFS_MINIO_FIXTURE_ROOT` or `../rio-v2/tests/fixtures/minio-generated`; `ManifestRecord` supplies bucket, object, and backend file paths. `load_file_info` reads object `xl.meta` and calls `rustfs_filemeta::get_file_info` with data and free-version inclusion. `encrypted_fixture_bytes` opens the fixture disk via `Endpoint` and `new_disk`, creates part readers with `create_bitrot_reader`, reads each part shard with checksum metadata, and concatenates encrypted object bytes. `assert_fixture_round_trip` then creates `ObjectInfo`, injects `__RUSTFS_SSE_SIMPLE_CMK`, constructs `GetObjectReader`, reads plaintext, and verifies offset, length, object size, byte count, and SHA-256.

State and persistence: this test reads fixture files under a MinIO disk layout and temporarily mutates process environment through `temp_env::async_with_vars`. It does not write repository state. Disk readers are explicitly closed.

Dependencies and integration: ties `ecstore` disk, bitrot, object read/decryption, `rustfs_filemeta`, `sha2`, `hex_simd`, `tokio`, `serde_json`, and the fixture-lab manifest contract together. It is a high-value cross-project compatibility guard for SSE-S3 and SSE-KMS MinIO data.

Risks: ignored tests can drift if fixtures are not regenerated in CI. Environment-variable KMS setup is brittle. The reader loop stops on a short read, so any future reader that returns short non-EOF reads could truncate test input. Fixture path assumptions depend on object names not requiring escaping beyond the manifest entries.

Test signals: two ignored Tokio tests cover `sse-s3-multipart-8m` and `sse-kms-multipart-8m`; success proves xl.meta decoding, bitrot reads, encrypted-object reader construction, and plaintext hash compatibility.
