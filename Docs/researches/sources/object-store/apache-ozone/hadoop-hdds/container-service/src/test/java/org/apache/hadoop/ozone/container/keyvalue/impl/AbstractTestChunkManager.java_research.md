# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/AbstractTestChunkManager.java

## Purpose
`AbstractTestChunkManager` is the shared fixture for chunk-manager implementation tests. It creates a formatted temporary `HddsVolume`, a real `KeyValueContainer`, default block/chunk/data fixtures, and reusable assertions for chunk file counts, file closure, and volume IO metrics.

## Important APIs, types, and functions
Subclasses implement `getStrategy()` returning `ContainerLayoutTestInfo`, which controls layout-specific configuration and chunk-manager construction. `createTestSubject()` builds a `BlockManagerImpl` and delegates to `getStrategy().createChunkManager(true, blockManager)`. Helper methods expose `KeyValueContainer`, `KeyValueContainerData`, `BlockID`, `ChunkInfo`, test `ByteBuffer`, and `BlockManager`.

## Control flow
The `@BeforeEach setUp` method configures the selected strategy, creates/formats an `HddsVolume`, mocks a `MutableVolumeSet` and `RoundRobinVolumeChoosingPolicy`, constructs `KeyValueContainerData` with configured layout, creates the container on disk, and initializes test bytes. The fixture stores a header prefix in the data buffer and positions the buffer after the header so chunk-manager writes test only the payload bytes.

## State and persistence behavior
Container directories, metadata paths, and chunk paths are real filesystem artifacts. `checkChunkFileCount` enumerates the chunk directory. `checkWriteIOStats` and `checkReadIOStats` assert volume-level byte/op counters. `checkChunkFilesClosed` uses `lsof` to verify chunk files are no longer open after finish/commit paths.

## Dependencies and integration points
The fixture integrates container layout abstraction, block manager persistence, volume formatting, volume choosing policy, JUnit temp directories, Mockito, and OS-level `lsof`. It underpins dummy, file-per-chunk, file-per-block, and shared chunk-manager tests.

## Risks and edge cases
The fixture itself can skip file-closure tests when `lsof` is unavailable by aborting. Incorrect buffer positioning would cascade into many chunk length assertions. Because it uses real volume stats, tests can catch regressions in IO accounting as well as filesystem layout.

## Test signals
Downstream tests rely on this fixture for exact file-count assertions, chunk data equality after rewinding to payload start, read/write op count checks, and detection of leaked file handles.
