# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/HddsVolumeFactory.java

Purpose: Factory for constructing normal and failed `HddsVolume` objects for data storage directories.

Important APIs and types: Extends `StorageVolumeFactory`; implements `createVolume` and `createFailedVolume`.

Control flow: Normal creation configures an `HddsVolume.Builder` with config, datanode UUID, cluster ID, usage factory, storage type, and parent set, then builds and validates cluster ID. Failed creation builds a failed placeholder from the raw location string.

State and persistence: No factory-local state beyond inherited constructor fields. Built volumes own VERSION, usage, DB, tmp, and metrics state.

Dependencies and integration points: Selected by `MutableVolumeSet` for `DATA_VOLUME`. It is the main bridge from configured storage locations to usable `HddsVolume` instances.

Risks: Failed placeholder construction uses the raw location string as storage directory, while normal construction parses `StorageLocation` before factory invocation. Tests should verify proper storage type propagation, failed-volume state, and cluster-ID consistency.
