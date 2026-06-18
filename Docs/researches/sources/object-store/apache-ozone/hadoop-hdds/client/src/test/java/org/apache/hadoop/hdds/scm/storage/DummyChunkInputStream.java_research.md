## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyChunkInputStream.java

**Purpose:** Provides a memory-backed `ChunkInputStream` test double that returns deterministic byte ranges split on checksum boundaries.

**Important APIs/types/functions:** The constructor delegates to `ChunkInputStream` with chunk metadata, block id, client factory, pipeline supplier, checksum flag, and a null token supplier, then clones the supplied chunk data. `readChunk(ChunkInfo)` reads `offset` and `len` from the request, slices `chunkData` into `ByteString` segments of `bytesPerChecksum`, stores those segments in `readByteBuffers`, and returns read-only `ByteBuffer` views through `BufferUtils`. `acquireClient()` and `releaseClient()` are no-ops. `getReadByteBuffers()` exposes the last low-level read segments.

**Control flow:** Higher-level `ChunkInputStream.read()` computes aligned `ChunkInfo` read requests; this override materializes exactly those requested segments locally. The recorded byte strings let tests verify how much backing data was fetched for partial reads.

**State and persistence:** Holds immutable-by-clone chunk data and a mutable list of the latest read segments, cleared on every `readChunk()` call. No persistence.

**Dependencies and integration points:** Integrates with `ChunkInputStream`, `BufferUtils`, protobuf `ChunkInfo`, Ratis third-party `ByteString`, and storage tests for checksum-boundary and seek behavior.

**Risks:** Does not exercise RPC client acquisition/release or token behavior. It assumes offsets/lengths fit into Java `int`, which is acceptable for the small test chunks.

**Test signals:** Strong signal for chunk seek/read algorithms, checksum-aligned fetching, buffer caching, and unbuffer behavior when paired with `TestChunkInputStream`.
