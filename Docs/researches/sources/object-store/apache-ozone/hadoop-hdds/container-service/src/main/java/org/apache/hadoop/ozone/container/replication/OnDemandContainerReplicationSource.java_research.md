# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/OnDemandContainerReplicationSource.java

Purpose: simple replication source that exports the current container to a tar stream on demand instead of prebuilding archives.

Important APIs and functions: `prepare` is a no-op. `copyData` resolves the container through `ContainerController`, throws `CONTAINER_NOT_FOUND` if absent, and delegates to `controller.exportContainer` with the container type, ID, destination stream, and `TarContainerPacker` configured for the requested compression.

Control flow and state: stateless apart from the controller reference. Every copy is generated fresh from current container files.

Dependencies and integration: used by `ReplicationServer` for pull downloads and can be passed to `PushReplicator` for source-side push streaming.

Risks and test signals: export consistency depends on the container's state and handler implementation. Tests should cover missing container result codes, compression propagation, output stream failure, and export of closed/quasi-closed/unhealthy containers according to controller policy.
