# sources/object-store/rustfs/crates/e2e_test/src/checksum_upload_test.rs

## Purpose
This e2e suite verifies S3 checksum handling for direct uploads and multipart uploads. It covers `Content-MD5`, `x-amz-checksum-sha256`, multipart per-part SHA-256 checksums, and CRC64NVME full-object checksum consistency between direct and multipart uploads.

## Important APIs, Types, and Functions
Helpers create an S3 client, create buckets idempotently, calculate base64 Content-MD5, calculate base64 SHA-256, and calculate CRC64NVME using `rustfs_rio::Checksum`. Tests use AWS SDK types `ChecksumAlgorithm`, `ChecksumMode`, `CompletedMultipartUpload`, and `CompletedPart`.

## Control Flow
Direct-upload tests compute the checksum, upload an object with the corresponding checksum header, then GET and compare bytes. The SHA-256 multipart test creates a multipart upload with checksum algorithm, uploads two 6 MiB parts with part checksums, carries returned checksum values into completed parts, completes the upload, and verifies concatenated bytes. The CRC64NVME test uploads the same full content directly and as two multipart parts, then HEADs both objects with checksum mode enabled and expects the same full-object checksum.

## State and Persistence
Each test starts a RustFS server, creates a bucket, and writes one or two objects. Multipart tests persist upload state until completion and then persisted object metadata/checksum state.

## Dependencies and Integration Points
The suite integrates RustFS checksum validation, AWS SDK checksum fields, multipart upload assembly, `rustfs-rio` checksum implementation, object metadata reporting via HEAD, and body retrieval via GET.

## Risks and Edge Cases
The tests mainly cover successful checksum paths; they do not assert rejection of incorrect checksums. Large 6 MiB parts make the tests slower but satisfy S3 multipart minimums. CRC64NVME correctness depends on `rustfs-rio` being the same algorithm expected by the server.

## Test Signals
Signals include successful Content-MD5 put/get, successful SHA-256 put/get, successful multipart upload with SHA-256 part checksums and exact body assembly, and equal CRC64NVME reported for direct and multipart objects.
