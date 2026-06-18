# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerLayoutTestInfo.java

Purpose: provides reusable test parameters and helpers for key-value container chunk layout implementations.

Important APIs/types/functions: enum values `DUMMY`, `FILE_PER_CHUNK`, and `FILE_PER_BLOCK`; `createChunkManager(boolean, BlockManager)`, `validateFileCount(File,long,long)`, `getLayout()`, `updateConfig(OzoneConfiguration)`, and the composite `@ContainerTest` annotation sourcing `ContainerLayoutVersion.getAllVersions`.

Control flow: each enum value constructs the matching `ChunkManager` implementation and asserts expected files under the chunks directory. `DUMMY` disables persisted data with `HDDS_CONTAINER_PERSISTDATA=false` and expects zero files. `FILE_PER_CHUNK` sets layout config and expects one file per chunk. `FILE_PER_BLOCK` sets layout config and expects one file per block.

State and persistence behavior: this helper controls whether tests write chunk data to disk and how many files should appear for a given block/chunk count. `updateConfig()` mutates the supplied `OzoneConfiguration` to align production code paths with the selected layout.

Dependencies and integration points: used by container integrity, mark-unhealthy, and reconciliation tests to run the same behavior over layout variants. It binds tests to `FilePerChunkStrategy`, `FilePerBlockStrategy`, `ChunkManagerDummyImpl`, and layout config keys.

Risks and test signals: centralizing layout setup keeps broad tests consistent. Because file-count assertions inspect only direct children, layout changes that add sidecar files in chunks directories would require updating this contract.
