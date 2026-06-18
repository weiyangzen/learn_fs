# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcReplicationClient.java

Purpose: gRPC client for datanode-to-datanode replication download and upload calls.

Important APIs and functions: the constructor builds a `ManagedChannel` with max inbound message size, optional mutual TLS from `SecurityConfig` and `CertificateClient`, no proxy detection, and a generated `IntraDatanodeProtocolServiceStub`. `download` sends a `CopyContainerRequestProto` for a whole container using configured compression, creates a destination tar path, and returns a `CompletableFuture<Path>` completed by `StreamDownloader`. `upload` exposes the generated bidirectional upload stream. `close` shuts the channel down with a five-second termination wait.

Control flow and state: `closed` prevents repeated shutdown. `StreamDownloader` creates parent directories and an output stream at construction, writes each response chunk to the stream, closes and completes on success, and closes/deletes/completes exceptionally on any stream or filesystem error.

Dependencies and integration: used by `SimpleContainerDownloader` and `GrpcContainerUploader`. It depends on generated datanode protocol stubs, Netty gRPC, TLS managers, and container tar naming utilities.

Risks and test signals: partial download cleanup and channel shutdown affect retry safety. Tests should cover TLS and plaintext setup, parent directory creation, onNext write failure deletion, onError cleanup, onCompleted close failure, repeated close, and compression request field propagation.
