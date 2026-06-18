# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerCompression.java

Purpose: enumerates supported compression codecs for container-copy streams and converts between configuration, protobuf, and wrapped Java streams.

Important APIs and functions: enum values are `NO_COMPRESSION`, `GZIP`, `LZ4`, `SNAPPY`, and `ZSTD`. `getConf(ConfigurationSource)` reads `HDDS_CONTAINER_REPLICATION_COMPRESSION` and falls back to no compression on invalid values. `setOn(ConfigurationTarget)` writes the enum to config. `toProto` and `fromProto` convert to `CopyContainerCompressProto`. `wrap(InputStream)` and `wrap(OutputStream)` use Apache Commons Compress except that `NO_COMPRESSION` returns the original stream.

Control flow and state: each enum stores the Commons Compress factory name. Unsupported configured or protobuf values do not fail replication setup; they degrade to no compression.

Dependencies and integration: passed through `GrpcReplicationClient`, `GrpcReplicationService`, `SendContainerOutputStream`, `SendContainerRequestHandler`, `TarContainerPacker`, pull download, and push upload paths.

Risks and test signals: codec availability and framing compatibility are critical because archives are packed and unpacked on different datanodes. Tests should cover each codec, invalid config fallback, null/unknown proto fallback, stream wrapping exception conversion, and mixed source/target compression negotiation.
