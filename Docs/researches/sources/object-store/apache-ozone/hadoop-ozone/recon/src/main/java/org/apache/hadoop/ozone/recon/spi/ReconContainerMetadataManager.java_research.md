## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconContainerMetadataManager.java

Purpose: this unstable SPI defines Recon DB operations for container-to-key metadata, container counts, container listings, reverse key-prefix lookups, and container replica history.

Important APIs and types: operations include `reinitWithNewContainerDataFromOm`, staged-manager creation, `reinitialize`, batch stores for container-key mappings and container key counts, replica history stores, count stores/increments, lookup APIs, iterators, deletion APIs, table accessors, and `commitBatchOperation`. Key types include `ContainerKeyPrefix`, `KeyPrefixContainer`, `ContainerMetadata`, `ContainerReplicaHistory`, `DatanodeID`, `DBStore`, `Table`, `TableIterator`, and `SeekableIterator`.

Control flow: OM reprocess tasks can rebuild mappings in bulk or via batches. API paths can page by container, key prefix, or reverse key-prefix index. Container manager code uses replica history methods to persist DataNode sightings and removal information.

State and persistence: implementations persist multiple Recon container metadata tables in RocksDB. Batch APIs allow atomic writes through `BatchOperation`/`RDBBatchOperation`. Staged managers support task reinitialization against a staged Recon DB before swap.

Dependencies and integration points: used by namespace/container tasks, Recon APIs, and `ReconContainerManager`. Codecs in this subset (`ContainerKeyPrefixCodec`, `KeyPrefixContainerCodec`) define key serialization for two of the tables.

Risks and edge cases: this is a broad interface with deprecated and current deletion paths. Callers must maintain consistency between forward mappings, reverse mappings, per-container counts, and total count. Iterator methods expose low-level table access and require caller-side close discipline.

Test signals: manager implementation tests should cover batch atomicity, staged reinitialization, forward/reverse lookup consistency, pagination, replica history merge behavior, deprecated deletion compatibility, and count drift.
