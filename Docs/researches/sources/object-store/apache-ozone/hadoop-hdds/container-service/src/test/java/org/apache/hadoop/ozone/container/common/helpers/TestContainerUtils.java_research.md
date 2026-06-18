# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/helpers/TestContainerUtils.java

Purpose: This suite covers utility behavior in `ContainerUtils`: debug redaction, container tar-name round trips, datanode ID persistence and recovery, protobuf-to-YAML upgrade reads, malformed ID handling, IP validation behavior, and disk-space admission metrics around hard and soft spare-space limits.

Important APIs and types: It uses `ContainerUtils`, `DatanodeIdYaml` indirectly through read/write helpers, `DatanodeVersionFile`, `DatanodeDetails`, `MockDatanodeDetails`, `ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `processForDebug`, `SpaceUsageSource.Fixed`, `HddsVolume`, `VolumeInfoMetrics`, and `StorageContainerException` with result `DISK_OUT_OF_SPACE`.

Control flow: Setup points metadata dirs at a temp directory. Redaction builds a read-chunk response containing known bytes and verifies the debug string keeps position while replacing data with the redacted string. ID persistence writes and reads `DatanodeDetails`, mocks DNS lookup to test persisted-vs-resolved IP handling, verifies cert serial and version fields, rejects missing and malformed files, and reads an older protobuf-format ID file. Recovery creates a VERSION file with a datanode UUID, creates an empty ID file, and expects `readDatanodeDetailsFrom` to reconstruct and rewrite it. Space tests mock volume free-space methods and metrics to cover soft-band, hard reject, equality boundaries, null metrics, zero-size writes, and disabled soft band.

State and persistence behavior: Persistent files include datanode ID YAML/protobuf files, malformed ID files, and VERSION files. Runtime state includes `DatanodeDetails` ports, IP validation, certificate serial ID, initial/current versions, and volume metrics counters. Disk-space tests do not use real disk state; they model available/capacity/used values through fixed usage objects and mocked spare-space methods.

Dependencies and integration points: These helpers are used during datanode startup, upgrade recovery, debugging logs, container archive naming, write-path disk admission, and metrics. The suite links configuration keys for metadata and datanode directories with storage volume VERSION recovery.

Risks: Mocked static DNS behavior must be scoped carefully. The recovery test assumes a specific `hdds/VERSION` layout under `HDDS_DATANODE_DIR_KEY`. Space admission tests encode strict less-than boundary semantics, so any intentional policy change must update several assertions.

Test signals: Redacted debug string position, tar name ID recovery, full datanode details equality including protobuf form, malformed/missing file exceptions, recovered UUID and rewritten ID file, `DISK_OUT_OF_SPACE` result on hard reject, correct metric increment paths, no null-metrics NPE, and no metric for zero-sized or exact-soft-boundary writes.
