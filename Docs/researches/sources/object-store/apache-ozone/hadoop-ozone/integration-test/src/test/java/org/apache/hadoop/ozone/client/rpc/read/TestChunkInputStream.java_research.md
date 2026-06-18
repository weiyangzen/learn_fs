<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestChunkInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestChunkInputStream.java

Purpose: This class validates `ChunkInputStream` buffering behavior, especially checksum-boundary caching and buffer release, across container layout versions.

Important APIs/types/functions: It extends `TestInputStreamBase`, runs under `ContainerLayoutTestInfo.ContainerTest`, and uses `TestBucket`, `KeyInputStream`, `BlockInputStream`, `ChunkInputStream`, `ByteBuffer`, `IOUtils.readFully`, and layout updates through the base class.

Control flow: `testAll` opens a client, applies the requested container layout, creates a test bucket, and runs three private tests. `testChunkReadBuffers` writes multi-block data, initializes the first block stream, reads one byte and larger spans from the first chunk, performs seeks across checksum boundaries, checks cached buffer counts/capacities/null slots, and verifies buffers are released after EOF. `testBufferRelease` reads up to the last byte of a checksum buffer, confirms it remains cached, reads the last byte, confirms release, then reads more data and checks a new buffer is used. `testCloseReleasesBuffers` confirms explicit close clears cached buffers.

State and persistence behavior: Persistent state is random key data in a test bucket. Runtime state under test is `ChunkInputStream.getCachedBuffers`, positions, remaining bytes, and cached `ByteBuffer` identity.

Dependencies and integration points: Integrates client read streams, block/chunk stream hierarchy, checksum sizing from `OzoneClientConfig`, container layouts, and `TestBucket` data validation.

Risks: The test asserts internal buffer-array shape, nulling, and capacity. Legitimate buffer implementation refactors may require test updates even if external reads remain correct.

Test signals: Passing means chunk reads fetch checksum-sized buffers, release consumed buffers promptly, preserve data correctness after seek/read, and free buffers on close or EOF.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestChunkInputStream.java -->
