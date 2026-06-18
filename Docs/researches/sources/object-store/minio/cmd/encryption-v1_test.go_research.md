<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/encryption-v1_test.go -->
## sources/object-store/minio/cmd/encryption-v1_test.go

Purpose: This file tests selected encryption behaviors for SSE-C request handling, object info decryption validation, ETag decryption, encrypted range calculation, and default encryption option inference.

Important APIs and functions: `TestEncryptRequest` exercises `EncryptRequest`. `TestDecryptObjectInfo` exercises `DecryptObjectInfo`. `TestDecryptETag` exercises `DecryptETag`. `TestGetDecryptedRange_Issue50` and `TestGetDecryptedRange` exercise `ObjectInfo.GetDecryptedRange`. `TestGetDefaultOpts` exercises `getDefaultOpts` with MinIO Go encryption types.

Control flow: `TestEncryptRequest` forces TLS, builds requests with SSE-C headers, encrypts a 64-byte reader, and asserts encryption metadata keys exist. `TestDecryptObjectInfo` runs table cases for unencrypted objects, encrypted metadata with GET/HEAD headers, missing SSE-C keys, invalid SSE-C parameters on unencrypted objects, and tampered encrypted sizes. `TestDecryptETag` checks successful unsealing, invalid hex, tampered encrypted ETags, and special multipart-style random ETags with `-partcount` suffixes. Range tests build encrypted object sizes via `sio.EncryptedSize`, use explicit `HTTPRangeSpec` cases, and compare production range translation to a reference implementation for multipart objects. `TestGetDefaultOpts` checks SSE-C, SSE-S3, existing metadata, copy-source behavior, and malformed keys.

State and persistence behavior: Tests are in-memory. They construct metadata maps and `ObjectInfo` values that mimic persisted encrypted object state. The range tests encode important persistence assumptions: stored sizes include DARE overhead and multipart parts are independently encrypted.

Dependencies and integration points: The tests depend on `minio-go/v7/pkg/encrypt`, `internal/crypto`, MinIO HTTP constants, `sio`, and human-size constants. They validate integration between request headers, object metadata, and crypto helpers.

Risks: KMS-backed encryption paths are mostly not exercised because no real or fake `GlobalKMS` is configured. Streaming decrypt readers, key rotation, encrypted checksum metadata, and multipart `DecryptBlocksReader` behavior are not directly read/compared. Some tests assert broad error equality and do not validate response-to-S3-error mapping.

Test signals: The range tests are strong because they cover single-part, multipart, suffix ranges, large part counts, package-boundary skips, and a named regression. The request and ETag tests provide focused compatibility coverage for common SSE-C and encrypted ETag edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/encryption-v1_test.go -->
