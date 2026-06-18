## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestChunkInputStream.java

**Purpose:** Tests `ChunkInputStream` data correctness, checksum-boundary-aligned reads, seek behavior, unbuffer behavior, and reconnection to a changed pipeline/token.

**Important APIs/types/functions:** `setup()` creates a 100-byte chunk with CRC32 checksums every 20 bytes and a `DummyChunkInputStream`. `testFullChunkRead()` and `testPartialChunkRead()` assert returned bytes and low-level fetched buffers. `testSeek()` validates EOF message, pre-read `chunkPosition`, cached-buffer seeks, outside-cache seeks, and boundary release behavior. `testSeekAndRead()` validates sequential reads after seeking. `testUnbuffered()` ensures `unbuffer()` releases buffers but preserves logical position. `connectsToNewPipeline()` uses mocked `XceiverClientFactory` and `XceiverClientSpi` with mutable pipeline/token suppliers, calls `unbuffer()`, swaps both suppliers, reads, and verifies the new pipeline and token are used.

**Control flow:** Reads consult cached aligned buffers when possible and issue aligned read requests otherwise. Seek either adjusts within cached data or records a new chunk position. Unbuffer clears buffers and forces the next read to reacquire a client.

**State and persistence:** Uses in-memory chunk bytes, checksum metadata, cached read buffers, current position, and mutable supplier references. No persistence.

**Dependencies and integration points:** Integrates with `ChunkInputStream`, `DummyChunkInputStream`, container command response builders, `ByteStringConversion`, `ChunkBuffer`, pipelines, tokens, Mockito, and JUnit.

**Risks:** Dummy read behavior avoids actual checksum failure and RPC error paths. `connectsToNewPipeline()` is sensitive to the precise order of unbuffer and supplier changes.

**Test signals:** Strong signal for chunk position/caching semantics and for pipeline/token refresh after unbuffering.
