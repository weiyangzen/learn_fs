## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RegisteredCommand.java

Purpose: `RegisteredCommand` models the response to a datanode register call. It returns the SCM registration result, the datanode identity, and the cluster ID.

Important APIs and types: the class wraps `SCMRegisteredResponseProto.ErrorCode`, `DatanodeDetails`, and cluster ID. `newBuilder()` returns a builder with `setDatanode`, `setClusterID`, `setErrorCode`, and `build`. `getProtoBufMessage()` emits `SCMRegisteredResponseProto`.

Control flow and state: the builder validates successful registrations: on `ErrorCode.success`, datanode, datanode UUID, and cluster ID must be present or `IllegalArgumentException` is thrown. Protobuf conversion always writes cluster ID, datanode UUID, and error code, and conditionally writes hostname, IP address, network name, and network location when non-empty.

Persistence and integration: this is transport response state for datanode registration. It integrates with SCM registration implementations, `DatanodeDetails`, and the `StorageContainerDatanodeProtocol` register path. No durable persistence happens in this class.

Risks and test signals: unsuccessful responses can be built with null datanode or cluster fields, but `getProtoBufMessage()` assumes `datanode` is non-null, so callers must avoid serializing incomplete failure responses or this can fail. The validation only covers success. There are no direct tests here, but `ScmTestMock.register()` constructs equivalent successful registration protobufs in test infrastructure.
