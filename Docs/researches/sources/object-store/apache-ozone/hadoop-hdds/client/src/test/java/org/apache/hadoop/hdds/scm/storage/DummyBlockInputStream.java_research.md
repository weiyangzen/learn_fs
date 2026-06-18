## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStream.java

**Purpose:** Provides a test double for `BlockInputStream` that avoids real datanode RPCs while preserving block/chunk read behavior for storage stream tests.

**Important APIs/types/functions:** The constructor delegates to `BlockInputStream` with a `BlockLocationInfo` built from a `BlockID` and length, plus pipeline, token, client factory, refresh function, and `OzoneClientConfig`. It stores a list of protobuf `ChunkInfo` entries and a map from chunk name to byte data. `getBlockData()` returns protobuf `BlockData` containing the injected chunks. `createChunkInputStream()` returns a `DummyChunkInputStream` over a clone of the mapped byte array. `checkOpen()` is overridden as a no-op.

**Control flow:** During test reads, `BlockInputStream.initialize()` obtains block metadata from the overridden `getBlockData()` and creates chunk streams through the overridden factory. Each chunk read uses local memory rather than RPC.

**State and persistence:** Holds in-memory chunk metadata and byte arrays. It clones per-chunk byte data before creating the dummy chunk stream, reducing accidental mutation between tests. No persistence.

**Dependencies and integration points:** Integrates with `BlockInputStream`, `BlockLocationInfo`, `DummyChunkInputStream`, protobuf container messages, pipeline/token/client factory types, and `OzoneClientConfig`.

**Risks:** The no-op `checkOpen()` bypasses close/open validation, so tests using it do not cover lifecycle failure behavior. Passing a null chunk map in specialized tests can be safe only when `createChunkInputStream()` is overridden.

**Test signals:** Enables focused tests for seeking, chunk boundary reads, and retry behavior without requiring a datanode or SCM.
