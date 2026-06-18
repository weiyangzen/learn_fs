## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ReplicatedBlockChecksumComputer.java

### Purpose
`ReplicatedBlockChecksumComputer` computes a block checksum for replicated blocks from per-chunk checksum data.

### Important APIs and Types
It stores a list of container `ChunkInfo`. `compute` dispatches by combine mode. Static `digest(ByteBuffer)` returns an `MD5Hash`. `computeMd5Crc` creates the MD5 of all chunk checksum bytes. `computeCompositeCrc` composes per-chunk CRCs into a block CRC.

### Control Flow
MD5 mode concatenates all checksum `ByteString`s from every chunk and digests the concatenated bytes. Composite CRC mode determines checksum type from the first chunk, creates a block-level composer with chunk length as the stripe size, then for each chunk creates a chunk-level composer using bytes-per-CRC and feeds each checksum int with the remaining chunk byte count. The resulting chunk CRC is fed into the block composer with the chunk length.

### State and Persistence Behavior
The object only sets the inherited output buffer. It does not mutate input chunk metadata or persist state.

### Dependencies and Integration Points
It depends on container chunk checksum metadata, Hadoop `DataChecksum`, `MD5Hash`, `CrcComposer`, and protobuf `ByteString`. It is created by `ReplicatedFileChecksumHelper`.

### Risks and Edge Cases
Composite CRC has a suspicious precondition: `remainingChunkSize <= checksums.size() * chunkSize`, which uses chunk length where bytes-per-CRC would usually be expected. Unsupported checksum types throw. Building a concatenated `ByteString` repeatedly can be inefficient for many chunks.

### Test Signals
Tests should cover MD5 for multiple chunks/checksums, composite CRC for CRC32 and CRC32C, partial final checksum length handling, unsupported checksum type rejection, empty chunk list rejection in composite mode, and performance-sensitive large chunk lists if relevant.
