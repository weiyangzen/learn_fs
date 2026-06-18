# sources/object-store/rustfs/crates/e2e_test/src/compression_test.rs

## Purpose
This integration test verifies object compression round-trip behavior: RustFS stores a compressible object physically smaller than its logical content while HEAD and GET preserve the original object size and bytes.

## Important APIs, Types, and Functions
`generate_compressible_data` repeats a pattern to make a compressible byte vector. `find_part_files` recursively scans the bucket directory for physical `part.*` files containing the object key. `start_rustfs_with_compression` starts RustFS with `RUSTFS_COMPRESSION_ENABLED=true` and waits for TCP readiness.

## Control Flow
The test starts a compression-enabled server, creates a bucket, uploads a compressible object larger than `MIN_COMPRESSIBLE_SIZE`, checks HEAD `Content-Length`, scans physical part file sizes, asserts physical size is smaller than logical size, downloads the object, and checks length and byte equality.

## State and Persistence
State includes temporary RustFS object storage, a bucket, one object, and physical compressed part files under the temp directory. The test directly inspects on-disk storage layout.

## Dependencies and Integration Points
It integrates server environment configuration, S3 PutObject/HeadObject/GetObject, RustFS compression persistence, and local filesystem layout of object parts.

## Risks and Edge Cases
The test depends on current disk layout and `part.*` naming, so storage-layout refactors can break it even if S3 behavior remains correct. `start_rustfs_with_compression` waits for TCP only, unlike the stronger common readiness check. The environment variable name differs from archive compression tests, so config naming should be watched.

## Test Signals
Signals are original HEAD length, smaller summed physical part size, exact downloaded length, and byte-for-byte equality with uploaded data.
