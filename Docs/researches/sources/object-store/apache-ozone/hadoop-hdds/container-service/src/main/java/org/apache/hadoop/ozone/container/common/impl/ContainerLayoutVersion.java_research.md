<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerLayoutVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerLayoutVersion.java

Purpose: enum describing chunk-file layout versions for containers.

Important APIs and control flow: `FILE_PER_CHUNK` maps a chunk to a file named by chunk name and is deprecated. `FILE_PER_BLOCK` maps all chunks of a block to a single `<localID>.block` file and is the default. `getContainerLayoutVersion` looks up by numeric version, `getAllVersions` exposes all enum values, and `getConfiguredVersion` reads the configured enum while falling back to default on invalid config. Instance `getChunkFile` resolves file paths either from a provided chunk directory or from `ContainerData` via `ContainerUtils.getChunkDir`.

State and persistence: layout version number and description are persisted in container metadata and determine on-disk chunk layout. The enum itself is immutable.

Dependencies and integration: used by `ContainerData`, `ContainerDataYaml`, key-value container IO, and block/chunk handlers. Depends on `BlockID`, configuration source, SCM config keys, and container utility path validation.

Risks and test signals: tests should cover both layout path derivations, invalid config fallback, unknown persisted layout returning null, and behavior when the chunk directory is missing. New layouts require backward-compatible YAML and chunk lookup handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerLayoutVersion.java -->
