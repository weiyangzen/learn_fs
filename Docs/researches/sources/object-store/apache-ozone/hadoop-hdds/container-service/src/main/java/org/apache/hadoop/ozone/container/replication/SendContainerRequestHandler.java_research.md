# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerRequestHandler.java

Purpose: receives a pushed container archive over gRPC, writes it to a temporary tarball on a selected volume, and imports it when the upload completes.

Important APIs and functions: `onNext` validates message offset, rejects existing/in-progress imports, initializes container ID, compression, reservation size, volume, temp directory, tar path, and output stream on the first message, writes data, advances `nextOffset`, and releases zero-copy buffers. `onError` closes and deletes the partial tarball, reports the gRPC error, and releases committed bytes. `onCompleted` closes output, calls `ContainerImporter.importContainer`, sends an empty success response, completes the response stream, or deletes the tarball and reports an error on import failure.

Control flow and state: `containerId == -1` identifies the uninitialized state. `nextOffset` enforces in-order chunks. `spaceToReserve` is based on the first request's size field when present. Volume committed bytes are decremented in both error and completion paths.

Dependencies and integration: created by `GrpcReplicationService.upload`; relies on `ContainerImporter`, `ContainerUtils`, `HddsVolume`, and Ratis zero-copy marshaller.

Risks and test signals: recursive `onError` from `onNext` can interact with later stream callbacks, and `onCompleted` with no parts returns without completing the response. Tests should cover offset mismatch, duplicate import rejection, first-message size reservation, partial file cleanup, successful import response, marshaller release, and committed-byte balance.
