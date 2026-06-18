# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumCache.java

## Purpose
`ChecksumCache` caches checksums for a growing `ChunkBuffer` so repeated checksum computation during writes only recomputes the last partial checksum and newly appended checksum segments.

## Important APIs, types, and functions
- Constructor accepts `bytesPerChecksum`, initializes `prevChunkLength` to zero, and preallocates the checksum list based on a 4 MB block chunk size hint.
- `clear()` resets previous length and removes all cached checksums.
- `getChecksums()` returns the backing checksum list.
- `computeChecksum(ChunkBuffer data, Function<ByteBuffer, ByteString> function)` computes or updates checksum entries for data up to `data.limit()`.

## Control flow
If current chunk length equals the previous length, the cached list is returned. If current length is smaller, an `IllegalArgumentException` signals that the caller failed to clear cache for a new chunk. Otherwise, the method calculates the first checksum index needing recomputation from `prevChunkLength / bytesPerChecksum`, iterates `data.iterate(bytesPerChecksum)`, skips known stable entries, updates the previous last partial entry or appends new entries, verifies the expected end index, updates `prevChunkLength`, and returns the list.

## State and persistence behavior
State is mutable and in-memory: `prevChunkLength` and the backing `List<ByteString>`. The returned list is mutable and owned by the cache. No persistence exists, but its output is used to build persisted `ChecksumData`.

## Dependencies and integration points
It depends on `ChunkBuffer`, `Checksum.computeChecksum`, and Ratis `ByteString`. It is currently intended for `BlockOutputStream` through `Checksum` when cache use is explicitly requested.

## Risks and edge cases
- The cache is not thread-safe.
- Callers must clear it when starting a new block chunk; otherwise smaller lengths throw and equal/larger unrelated data can produce wrong reuse.
- `getChecksums()` exposes mutable internal state.
- `bytesPerChecksum` must be positive; no constructor validation is present.
- The algorithm recomputes the last partial checksum rather than incrementally extending CRC state, which is correct but leaves some performance on the table.

## Test signals
Tests should cover repeated same-length calls, append within a partial checksum, append crossing checksum boundaries, exact boundary lengths, shrink-without-clear exception, clear behavior, output equality with full recomputation, and invalid `bytesPerChecksum` handling.
