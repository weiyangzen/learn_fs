# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicationSource.java

Purpose: abstracts the source side of container replication, allowing implementations to prepare and stream a binary representation of a container.

Important APIs and types: `prepare(long containerId)` gives a source implementation a chance to precompute or cache an archive. `copyData(long containerId, OutputStream destination, CopyContainerCompression compression)` writes the full container representation to the destination stream.

Control flow and state: none in the interface. The concrete on-demand implementation does no pre-work and exports directly when `copyData` is invoked.

Dependencies and integration: consumed by `GrpcReplicationService.download` for pull replication and `PushReplicator` for push replication. Compression is passed in so the source and destination agree on archive encoding.

Risks and test signals: callers assume `copyData` writes a complete valid container archive or throws. Tests should exercise missing containers, compression compatibility, stream close behavior, and any implementation-specific caching invalidation.
