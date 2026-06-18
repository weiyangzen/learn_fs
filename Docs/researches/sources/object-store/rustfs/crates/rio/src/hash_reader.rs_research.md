<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hash_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/hash_reader.rs

## Purpose
Provides the main request-body validation reader for RustFS object I/O. `HashReader` composes length enforcement, MD5/ETag handling, SHA-256 verification, S3 checksum validation or calculation, and trailing checksum extraction around a dynamic async reader.

## Important APIs, types, and functions
- `HashReader::from_stream`, `from_reader`, and `new` construct wrappers for plain, capability-aware, or already boxed readers.
- `HashReaderMut` exposes mutable parameters and inner-reader extraction for nested wrapping.
- `add_checksum_from_s3s`, `add_checksum_no_trailer`, `add_non_trailing_checksum`, and `add_calculated_checksum` configure checksum behavior.
- `checksum`, `content_crc_type`, and `content_crc` expose validated/calculated checksum metadata.
- `AsyncRead::poll_read` updates hashers and finalizes validation at EOF.

## Control flow
Construction wraps positive-size streams in `HardLimitReader` and, unless `diskable_md5` is set, `EtagReader`. `new` detects an existing unread `HashReader` through `HashReaderDetector`, validates compatible size/checksum metadata, transfers its inner reader, and preserves checksum/trailer state. During reads, newly filled bytes increment `bytes_read` and feed optional SHA-256 and content-checksum hashers. On the first EOF, it compares SHA-256, loads trailing checksum headers if needed, calculates content checksums, fills missing calculated checksum values, or returns `ChecksumMismatch` wrapped in `InvalidData`.

## State and persistence behavior
The reader stores expected size, actual size, optional MD5, checksum selection and values, optional trailing headers, byte count, and one-shot EOF validation state. It does not persist directly, but the resulting ETag and content checksum maps are object metadata signals and the length/checksum validations decide whether incoming data is acceptable.

## Dependencies and integration points
Depends on local checksum types and hashers, `HardLimitReader`, `EtagReader`, reader capability traits, `s3s::TrailingHeaders`, HTTP headers, base64, `hex_simd`, and Tokio `AsyncRead`. It is intended for S3 PUT/upload/copy paths, trailer-aware checksums, and transformation layers such as compression/encryption using `SIZE_PRESERVE_LAYER`.

## Risks and edge cases
Wrapping an already-read `HashReader` is rejected, but nested wrapper state transfer is subtle and can lose behavior if new wrappers do not implement capability traits. SHA-256 mismatches currently return a generic string rather than the typed `Sha256Mismatch`. Trailer checksums are read only at EOF, so missing or malformed trailer values surface late. `diskable_md5` suppresses ETag resolution and must align with callers that compute MD5 elsewhere.

## Test signals
Tests cover wrapper construction, boxed capability delegation, boxed encrypt-reader inputs, basic ETag generation, diskable MD5 suppression, calculated CRC64 metadata, wrapping an existing `HashReader`, compression/encryption round trips, compressible data, and gzip/deflate/zstd compression algorithms.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hash_reader.rs -->
