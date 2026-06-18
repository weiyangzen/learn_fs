## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockInputStream.java

**Purpose:** Tests `BlockInputStream` seek/read behavior across chunk boundaries, byte-array and `ByteBuffer` reads, retry/refresh rules, and unbuffered client release behavior.

**Important APIs/types/functions:** `setup()` builds five chunks of size 100 except the last at 50 bytes, disables checksum verification, and creates a `DummyBlockInputStream`. `createChunkList()` constructs protobuf `ChunkInfo` entries and a concatenated `blockData` oracle. `testSeek()`, `testRead()`, `testReadWithByteBuffer()`, `testReadWithDirectByteBuffer()`, and `testSeekAndRead()` validate position, chunk index, EOF, and data correctness. `testRefreshPipelineFunction()` uses `DummyBlockInputStreamWithRetry` and log capture to verify retry after a first failure. Parameterized tests distinguish exceptions that trigger refresh (`StorageContainerException(CONTAINER_NOT_FOUND)` and gRPC `UNAVAILABLE` wrapped in `ExecutionException`) from exceptions that do not (`SCMSecurityException`, checksum exception, generic `IOException`). `testRefreshOnReadFailureAfterUnbuffer()` ensures unbuffer releases the old read client before retrying with a refreshed pipeline.

**Control flow:** Reads start uninitialized, so early seeks update block position until initialization maps the position to a chunk index. Reads span chunks and update stream position. Retry tests force failures either in block metadata retrieval or chunk reads, then assert refresh function invocation and subsequent success only for whitelisted failure types.

**State and persistence:** Uses in-memory byte arrays, chunk metadata, mocked refresh function, and client factory mocks. No persistence. Internal stream state under test includes block position, chunk index, initialized state, and client references after unbuffer.

**Dependencies and integration points:** Depends on `BlockInputStream`, dummy stream classes, `BlockExtendedInputStream` logs, `XceiverClientFactory`, `XceiverClientSpi`, `MockPipeline`, protobuf messages, Ozone checksum classes, gRPC status classes, Mockito, AssertJ, and JUnit.

**Risks:** The dummy stream bypasses some real client lifecycle behavior, though `testRefreshOnReadFailureAfterUnbuffer()` covers release/acquire with the real base class. Random seek positions add coverage but can make exact failures less reproducible if a future bug is position-dependent.

**Test signals:** High-value unit signal for block read correctness, retry classification, and resource release around unbuffer and pipeline refresh.
