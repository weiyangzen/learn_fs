# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationService.java

Purpose: server-side gRPC service exposing datanode replication download and upload methods.

Important APIs and functions: `bindServiceWithZeroCopy` rebuilds the generated service definition so upload and download request marshallers use Ratis `ZeroCopyMessageMarshaller`, preserving any other methods unchanged. `download` converts compression from proto, wraps the response observer in `CopyContainerResponseStream`, and asks `ContainerReplicationSource.copyData` to stream the archive. `upload` creates a `SendContainerRequestHandler` that receives pushed archive chunks and imports the result.

Control flow and state: `BUFFER_SIZE` is 1 MiB. Download cleanup closes the output stream and releases the zero-copy request. Upload lifecycle is delegated to the request handler, which also releases per-message zero-copy buffers.

Dependencies and integration: instantiated by `ReplicationServer` with `OnDemandContainerReplicationSource` and `ContainerImporter`. It depends on generated `IntraDatanodeProtocolServiceGrpc` methods and Ratis zero-copy marshalling.

Risks and test signals: zero-copy release must happen even on errors, and server errors must translate to gRPC failures without leaking streams. Tests should cover download success, missing container error, compression conversion, zero-copy service descriptor replacement, upload handler creation, and cleanup when `source.copyData` throws.
