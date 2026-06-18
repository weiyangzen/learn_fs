# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerIntegrityChecks.java

Purpose: shared base fixture for key-value container integrity and metadata-inspector tests, with helpers to create containers containing normal and deleting blocks plus optional on-disk chunk data.

Important APIs/types/functions: `initTestData(ContainerTestVersionInfo)`, private `setup()`, `teardown()`, `getChunkLayout()`, `getConf()`, and `createContainerWithBlocks(long,int,int,boolean)`. Constants define `UNIT_LEN`, `CHUNK_LEN`, and `CHUNKS_PER_BLOCK`.

Control flow: `initTestData()` configures schema V3 state, maps layout versions to `ContainerLayoutTestInfo.FILE_PER_BLOCK` or `FILE_PER_CHUNK`, then sets up datanode and metadata directories. `createContainerWithBlocks()` creates a `KeyValueContainer`, opens its DB, generates deterministic block/chunk metadata, optionally writes and commits chunk bytes through the selected `ChunkManager`, and stores normal block keys first followed by deleting block keys.

State and persistence behavior: when `writeToDisk` is true, chunks are physically written using checksummed random ASCII bytes and file-count assertions validate layout-specific persistence. Block metadata is stored in RocksDB under normal or deleting key prefixes. Container max size is derived from total block/chunk bytes, with a minimum of 1 for empty containers.

Dependencies and integration points: depends on `ContainerLayoutTestInfo`, `ContainerTestVersionInfo`, `MutableVolumeSet`, `BlockUtils`, checksum computation, `ChunkManager` strategies, and `ContainerTestUtils` write/commit stages. Subclasses reuse it for scanner and metadata repair coverage.

Risks and test signals: provides consistent fixture generation across schema/layout variants. It assumes all non-file-per-block layouts in this suite should use file-per-chunk behavior; adding a new layout may require updating the mapping.
