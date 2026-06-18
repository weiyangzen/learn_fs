# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/StorageVolumeFactory.java

Purpose: Abstract base factory for data, metadata, and DB volume factories. It holds construction dependencies and enforces cluster-ID consistency for volumes with VERSION files.

Important APIs and types: Provides getters for `ConfigurationSource`, `SpaceUsageCheckFactory`, `VolumeSet`, datanode UUID, and cluster ID. Defines abstract `createVolume` and `createFailedVolume`. `checkAndSetClusterID` validates discovered cluster IDs.

Control flow: When the first created volume reports a cluster ID and the factory does not already have one, the factory adopts it. Later volumes must match or an `InconsistentStorageStateException` is thrown.

State and persistence: Factory-local state is in-memory only; persistent VERSION creation and reading belong to `StorageVolume`.

Dependencies and integration points: Concrete factories are selected by `MutableVolumeSet`. Cluster-ID validation prevents mixing directories from different Ozone clusters within the same data/DB volume set.

Risks: The cluster ID field mutates based on the first volume, so creation order can determine the adopted ID when no cluster ID was provided. Tests should cover null initial cluster ID, matching IDs, mismatched IDs, and failed-volume creation bypass behavior in concrete factories.
