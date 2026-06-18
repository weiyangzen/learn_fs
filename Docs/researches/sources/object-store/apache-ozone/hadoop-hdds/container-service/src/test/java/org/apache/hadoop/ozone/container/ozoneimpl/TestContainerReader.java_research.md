# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerReader.java

## Purpose
`TestContainerReader` validates datanode startup loading of key-value containers from disk. It checks metadata reconstruction, pending-delete counters, committed-space accounting, load-exception handling, invalid DB handling, parallel volume readers, duplicate/conflicting container resolution, deleted/recovering cleanup, EC replica-index selection, and checksum restoration.

## Important APIs, types, and functions
The suite exercises `ContainerReader.run`, `readVolume`, `KeyValueContainer.create`, `BlockUtils.getDB`, `ContainerCache.shutdownCache`, `ContainerSet`, `WitnessedContainerMetadataStore`, `ContainerCreateInfo`, and checksum helpers. It manipulates `DatanodeStoreSchemaOneImpl`, `DatanodeStoreSchemaTwoImpl`, and `DatanodeStoreSchemaThreeImpl` delete/block/metadata tables, plus `ContainerChecksumTreeManager` and `KeyValueHandler.updateContainerChecksum`.

## Control flow
Setup creates a real `HddsVolume`, two containers, block metadata, and pending-deletion records using schema-specific table formats. Reader tests start `ContainerReader` threads and join them, then inspect loaded container data. Multi-reader tests configure ten volumes, create 100 containers with deliberate conflicts, start one reader per volume, and verify winner selection. Checksum tests create containers with Merkle tree sidecars, no sidecars, or empty sidecars before reader startup.

## State and persistence behavior
The reader must reconstruct `blockCount`, `bytesUsed`, pending-delete block count/bytes, BCSID, committed-space flags, replica indexes, and data checksums from disk. Invalid or missing DB paths prevent loading and committed-byte increases. Marked `DELETED` containers are removed and their schema-v3 DB metadata entries are cleaned up. Ratis replicated `RECOVERING` containers are deleted on startup, while EC recovering containers can be marked unhealthy.

## Dependencies and integration points
This file spans container disk layout, volume sets, DB schema versions, container-create metadata, deleted-block transaction tables, container cache behavior, EC replica metadata, and checksum sidecar/RocksDB fallback. It is one of the strongest startup integration tests in this subset.

## Risks and edge cases
Risks include loading duplicate containers nondeterministically, deleting the wrong duplicate, ignoring higher BCSID or closed-state preference, mishandling EC replicas with same/different replica indexes, leaving deleted containers on disk or in DB, counting committed space for containers that failed to load, and failing to populate data checksum from Merkle trees or fallback metadata.

## Test signals
Signals include container counts, existence/removal of conflicting paths, committed-byte totals, container state assertions, replica-index assertions, cache size remaining zero, RocksDB metadata key counts, log text for missing DBs, and `verifyAllDataChecksumsMatch` across checksum scenarios.
