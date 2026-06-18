# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestChunkManagerDummyImpl.java

## Purpose
This small suite validates the dummy chunk-manager strategy used by tests or non-persistent paths. It confirms the dummy implementation accepts writes without creating files and returns non-null data for reads regardless of underlying chunk existence.

## Important APIs, types, and functions
The class extends `AbstractTestChunkManager`, selects `ContainerLayoutTestInfo.DUMMY`, and calls `ChunkManager.writeChunk` and `readChunk`. It uses the shared fixture block ID, chunk info, prepared data buffer, and `WRITE_STAGE`.

## Control flow
`dummyManagerDoesNotWriteToFile` creates the dummy subject, writes the fixture chunk, and immediately checks that the chunk directory remains empty. `dummyManagerReadsAnyChunk` reads from the dummy manager without preparing a file and asserts the returned `ChunkBufferToByteString` is non-null.

## State and persistence behavior
The intended behavior is explicitly non-persistent. The container and chunk directory exist because the abstract fixture creates them, but dummy writes do not create chunk files and dummy reads do not depend on filesystem state.

## Dependencies and integration points
The suite depends on the shared chunk-manager fixture for a real container context while checking that the dummy strategy bypasses real storage effects. This protects tests or flows that intentionally use a no-op chunk implementation.

## Risks and edge cases
The main risk is a dummy implementation accidentally inheriting real file-writing behavior or returning null on reads, which would break tests expecting non-storage semantics.

## Test signals
Signals are simple but precise: chunk file count remains zero after write, and read returns a non-null buffer object.
