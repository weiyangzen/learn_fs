## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStreamWithRetry.java

**Purpose:** Extends `DummyBlockInputStream` to simulate a first metadata-read failure and verify pipeline refresh/retry behavior in `BlockInputStream`.

**Important APIs/types/functions:** The constructor installs a refresh function that sets an `AtomicBoolean`, builds a mocked `BlockLocationInfo`, and returns a fresh single-node `MockPipeline`. It accepts an optional `IOException` to throw on the first `getBlockData()` call. `getBlockData()` increments `getChunkInfoCount`; on the first call it throws the injected exception or a `StorageContainerException` with `CONTAINER_NOT_FOUND`, then delegates to the parent on later calls.

**Control flow:** The first block-data fetch fails, causing the production read code to invoke its refresh logic. The retry call succeeds because subsequent `getBlockData()` calls return the in-memory chunk list.

**State and persistence:** Tracks a per-instance integer counter and injected exception. The external `AtomicBoolean` records refresh invocation for assertions. No persistence.

**Dependencies and integration points:** Depends on Mockito, `StorageContainerException`, `MockPipeline`, protobuf container types, and the parent dummy stream. Integrates with retry tests in `TestBlockInputStream`.

**Risks:** The counter is not thread-safe beyond test usage. Refresh-function behavior is synthetic and always returns a mock pipeline, so it cannot validate real SCM location semantics.

**Test signals:** Provides targeted signal that `CONTAINER_NOT_FOUND` and selected transport failures cause refresh and retry rather than immediate failure.
