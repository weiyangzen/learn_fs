# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/Checksum.java

## Purpose
`Checksum` computes and verifies per-chunk checksums for Ozone data buffers. It supports `NONE`, `CRC32`, `CRC32C`, `SHA256`, and `MD5`, splits data by `bytesPerChecksum`, and optionally uses `ChecksumCache` to avoid recomputing unchanged chunk segments.

## Important APIs, types, and functions
- Constructors accept checksum type, bytes per checksum, and optional cache enablement.
- `clearChecksumCache()` resets cache state when a new block chunk begins.
- `computeChecksum` overloads accept byte arrays, `ByteBuffer`, `List<ByteString>`, and `ChunkBuffer`, with optional cache use.
- `Algorithm` maps `ContainerProtos.ChecksumType` to functions backed by `MessageDigest` or `ChecksumByteBuffer`.
- `computeChecksum(ByteBuffer, Function, int)` temporarily limits a buffer to compute at most one checksum segment.
- Static verification helpers include `verifySingleChecksum`, `verifyChecksum(ByteBuffer, ChecksumData, int)`, `verifyChecksum(ChunkBuffer, ChecksumData, int)`, and `verifyChecksum(List<ByteString>, ChecksumData, int)`.
- `getNoChecksumDataProto()` returns a testing protobuf with checksum type `NONE`.

## Control flow
Computation short-circuits for `NONE`. Other types create a fresh algorithm function, wrap input in a read-only `ChunkBuffer`, iterate slices of `bytesPerChecksum`, compute one digest/checksum per slice, and return immutable `ChecksumData`. With cache enabled and requested, computation delegates to `ChecksumCache`, which recomputes only changed trailing checksum entries. Verification recomputes checksums for supplied data and delegates comparison to `ChecksumData.verifyChecksumDataMatches` with a start index.

## State and persistence behavior
Instances hold checksum type, bytes-per-checksum, and optional mutable cache. The class itself does not persist data, but `ChecksumData` output is serialized into container protobufs and stored/transmitted with chunk metadata.

## Dependencies and integration points
It depends on container protobuf `ChecksumType`, Ratis protobuf `ByteString`, `ChunkBuffer`, `BufferUtils`, `ChecksumByteBufferFactory`, `ChecksumCache`, `ChecksumData`, `IntegerCodec`, and `UnsafeByteOperations`. It integrates with Ozone clients, block streams, datanode chunk IO, and tests.

## Risks and edge cases
- The class is explicitly not thread-safe because algorithm functions and cache state are mutable.
- `bytesPerChecksum` must be positive for meaningful slicing; this class does not validate all invalid values directly.
- `computeChecksum(ByteBuffer, Function, int)` mutates and restores buffer limit but advances position through the algorithm.
- `verifySingleChecksum` sets limit to `offset + bytesPerChecksum`; callers must ensure bounds for short final chunks.
- MD5/SHA256 use a shared `MessageDigest` inside each function instance, so the function must not be shared concurrently.
- Cache correctness requires callers to clear cache whenever starting a new block chunk.

## Test signals
Tests should cover all checksum types, byte array/ByteBuffer/ChunkBuffer/List inputs, final partial chunk handling, start-index verification, mismatch exceptions, `NONE` short-circuit, read-only and direct buffers, cache reuse and cache clearing, invalid algorithm/type handling, and Java-version-specific CRC32C paths through the factory.
