<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/etag_reader.rs

## Purpose
Implements an `AsyncRead` wrapper that computes an MD5 ETag while bytes pass through and optionally verifies the final MD5 against an expected checksum.

## Important APIs, types, and functions
- `EtagReader<R>` stores `inner`, `md5`, `finished`, `checksum`, and cached `resolved_etag`.
- `new` constructs the wrapper.
- `get_etag` finalizes a clone of the MD5 state once and caches the hex result.
- `AsyncRead::poll_read` updates the hasher and validates at EOF.
- Implements `EtagResolvable`, `HashReaderDetector`, and `TryGetIndex`.

## Control flow
`poll_read` returns EOF immediately after `finished` is set. Otherwise it records the buffer's existing filled length, polls the inner reader, and hashes only newly appended bytes. A zero-byte successful read is treated as EOF: it finalizes or reuses the ETag and compares it with `checksum` if present. Mismatches return `InvalidData`.

## State and persistence behavior
The reader maintains only in-memory hashing state. The persisted value is indirect: after stream completion, the MD5 hex string can become object metadata or be compared to client-provided Content-MD5/ETag expectations. `resolved_etag` prevents repeated calls from changing the observed value.

## Dependencies and integration points
Depends on `md5`, `hex_simd`, `pin_project_lite`, Tokio `AsyncRead`, and `tracing`. `HashReader` wraps streams in `EtagReader` when MD5 is not disk-deferred. Compression/encryption wrappers delegate ETag discovery through it.

## Risks and edge cases
Calculated ETags are unavailable until EOF unless an expected checksum was supplied, in which case `try_resolve_etag` returns that checksum early. Callers that need the actual computed MD5 must ensure the stream is fully consumed. MD5 is not a cryptographic integrity guarantee by itself, so stronger checksums handled by `HashReader` remain important.

## Test signals
Tests cover basic MD5 calculation, empty streams, repeated resolution, partial unread streams returning `None`, large random data, successful checksum verification, and checksum mismatch returning `InvalidData`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag_reader.rs -->
