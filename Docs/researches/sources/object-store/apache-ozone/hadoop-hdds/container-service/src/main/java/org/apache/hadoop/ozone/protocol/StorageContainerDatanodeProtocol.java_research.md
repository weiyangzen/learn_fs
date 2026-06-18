# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerDatanodeProtocol.java

Purpose: RPC interface for datanode-to-SCM communication using protobuf request/response types.

Important APIs and functions: `versionID` is 1. `getVersion` returns SCM version information. `sendHeartbeat` sends datanode heartbeat data and returns SCM commands, allowing `TimeoutException`. `register` registers a datanode with extended details, node report, full container report, pipeline report, and layout version info, returning registration response data.

Control flow and state: interface only; implementations own registration, heartbeat state, command generation, and version negotiation.

Dependencies and integration: annotated with SCM Kerberos principal and used by datanode state machine endpoint tasks. It carries `NodeReportProto`, `ContainerReportsProto`, `PipelineReportsProto`, and `LayoutVersionProto` built by `OzoneContainer` and related services.

Risks and test signals: RPC compatibility and protobuf evolution are key. Tests should cover version response conversion, heartbeat timeouts, registration with layout versions, security principal configuration, and compatibility with Recon's inherited interface.
