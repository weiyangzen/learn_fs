## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainer.java

Purpose: Tests `OzoneContainer` container-map rebuild, node report generation, committed-space reconstruction, missing-container tracking, and disk-full container creation failures across schema/layout variants.

Important APIs/types/functions: `ContainerTestVersionInfo.ContainerTest`, `MutableVolumeSet`, `RoundRobinVolumeChoosingPolicy`, `KeyValueContainer`, `KeyValueContainerData`, `OzoneContainer.buildContainerSet`, `gatherContainerUsages`, `getNodeReport`, `BlockUtils.getDB`, and helper methods `addBlocks`, `verifyCommittedSpace`, `mockHddsVolume`.

Control flow: `initTest` configures layout/schema, `setup` creates volume sets and DB instances, then tests format volumes, create containers, write block/chunk metadata into RocksDB tables, restart/rebuild `OzoneContainer`, and compare container counts, committed bytes, usage, and missing ID sets. Node report tests configure metadata/Ratis/container DB directories and assert report list sizes. Disk-full test consumes all volume capacity then expects `StorageContainerException` with `DISK_OUT_OF_SPACE`.

State and persistence behavior: Writes real temporary container directories and RocksDB metadata; deletes some container directories to validate missing-container persistence in `ContainerSet`. Committed-space expectations are tracked in `commitSpaceMap`.

Dependencies and integration points: Exercises storage volumes, schema V3 DB setup, key-value container layout, node reports, and low-level metadata tables.

Risks and test signals: Good integration signal for upgrade/restart-like rebuild paths. Random datanode IP and temporary disk usage can create environmental sensitivity. Mock-volume usage checks decouple container ID iteration from actual volume internals.
