## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/RefreshVolumeUsageCommand.java

Purpose: `RefreshVolumeUsageCommand` is a simple SCM command that asks a datanode to refresh disk usage information immediately.

Important APIs and types: it extends `SCMCommand<RefreshVolumeUsageCommandProto>`, returns command type `refreshVolumeUsageInfo`, emits a protobuf containing only `cmdId`, and has a static `getFromProtobuf()` factory.

Control flow and state: construction uses the default `SCMCommand` id allocator. `getProto()` builds `RefreshVolumeUsageCommandProto` with the current id. `getFromProtobuf()` only null-checks the protobuf and returns a new command, which means it does not preserve the incoming `cmdId`.

Persistence and integration: state is limited to inherited command metadata: id, term, token, and deadline. The command is transported over `StorageContainerDatanodeProtocolProtos` and is consumed by datanode command processing that refreshes volume usage metrics or caches.

Risks and test signals: the id-loss during protobuf reconstruction is a behavioral risk if command status tracking expects response status to reference the original SCM command id. There are no direct tests in this subset. Tests around command status reporting or refresh handling should assert that command identity is either intentionally irrelevant or preserved by an outer wrapper.
