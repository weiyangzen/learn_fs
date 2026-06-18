<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerUtils.java

Purpose: static utility surface for container-layer error conversion, datanode ID persistence and recovery, container metadata file checksums, file/path derivation, pending-delete counters, tar archive naming, and volume free-space enforcement.

Important APIs and control flow: `logAndReturnError` maps `StorageContainerException` to `ContainerCommandResponseProto` and logs closed/open-state failures at debug while warning on others. Datanode identity flows through `writeDatanodeDetailsTo`, `readDatanodeDetailsFrom`, YAML parsing via `DatanodeIdYaml`, fallback recovery from volume `VERSION` files, and final protobuf compatibility fallback. `verifyContainerFileChecksum` recomputes YAML checksums with the right container YAML representer, including EC replica-index handling. `getChunkDir`, `getContainerFile`, `retrieveContainerIdFromTarName`, `getPendingDeletionBlocks`, and `getPendingDeletionBytes` are shared by container IO, archiving, and block deletion. `assertSpaceAvailability` enforces hard minimum free space and records soft/hard metrics.

State and persistence: writes and rewrites the datanode ID file, reads `VERSION` properties, and mutates `ContainerData` checksum fields during verification. Disk behavior is sensitive to file deletion/recreation and directory creation failures.

Dependencies and integration: integrates with `DatanodeDetails`, `HddsServerUtil`, `HddsVolume`, `StorageVolumeUtil`, `ContainerDataYaml`, `KeyValueContainerData`, `ContainerSet`, `VolumeInfoMetrics`, and protobuf response builders.

Risks and test signals: recovery creates a minimal `DatanodeDetails` from UUID only, so tests should cover hostname/IP absence after corrupt ID files. `getContainerIDFromFile` parses a path returned by `getContainerNameFromFile`, which includes parent path and can fail if callers pass unexpected file layout. Checksum tests should cover disabled verification, stale checksum, EC replica index inclusion, and missing chunk directories. Space tests should assert hard rejection, metric increments, and soft-band metric behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerUtils.java -->
