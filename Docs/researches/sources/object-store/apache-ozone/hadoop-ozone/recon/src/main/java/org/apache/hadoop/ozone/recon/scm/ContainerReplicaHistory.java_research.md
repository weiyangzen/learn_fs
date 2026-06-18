## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistory.java

Purpose: tracks first/last observed times and replica metadata for a container replica on one datanode.

Important APIs/types/functions: constructor; getters/setters for BCS ID, last seen time, state, checksums; `getDataChecksum`; `fromProto`; `toProto`.

Control flow: null checksums are normalized to `ContainerChecksums.unknown()`. Proto conversion maps datanode UUID, times, BCS ID, state, and data checksum.

State and persistence: used as persisted/container-history value data via proto wrappers; it records observation history but does not guarantee continuous replica presence. Integrates with `DatanodeID`, `ContainerChecksums`, and protobuf `ContainerReplicaHistoryProto`.

Risks: first seen time and datanode ID are final and cannot be corrected after construction. Proto only persists data checksum, not richer checksum object fields if added later. Tests should cover null checksums, proto round-trip, last-seen updates, state changes, and unknown checksum behavior.
