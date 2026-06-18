<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerGrpc.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerGrpc.java

## Purpose

`XceiverServerGrpc` is the standalone, non-Ratis datanode container transport server. It creates and manages the Netty gRPC server, TLS configuration, read executor pools, IPC port registration, standalone pipeline reporting, and direct dispatcher submission. The complete 267-line file was read.

## Important APIs, Types, and Functions

The class implements `XceiverServerSpi`. Public APIs include the constructor, `start()`, `stop()`, `getIPCPort()`, `getServerType()`, `submitRequest(...)`, `isExist(...)`, and `getPipelineReport()`. It owns `Server`, `ContainerDispatcher`, `ThreadPoolExecutor` for chunk reads, `EventLoopGroup`, `DatanodeDetails`, and port state.

## Control Flow

The constructor chooses a configured or random IPC port, sizes read executors from configured read threads per volume times storage directory count, chooses epoll or NIO Netty event loops, builds a `GrpcXceiverService`, installs tracing interceptors, sets message size and connection keepalive/idle policy, and optionally enables gRPC TLS from `CertificateClient`. `start` starts the server, resolves random port assignment, and records the standalone port in `DatanodeDetails`. `stop` shuts down read executors, server, and event loop group. `submitRequest` imports tracing context, dispatches the command directly, and throws `StorageContainerException` on non-success responses.

## State and Persistence Behavior

The class owns transport lifecycle state (`isStarted`, port fields, executor/event-loop objects). It does not persist container data directly; `ContainerDispatcher` owns command persistence.

## Dependencies and Integration Points

Dependencies include Ozone config keys, `DatanodeConfiguration`, `HddsServerUtil`, Netty/gRPC shaded Ratis classes, OpenTelemetry tracing, `SecurityConfig`, `CertificateClient`, and `ContainerDispatcher`.

## Risks and Edge Cases

If `poolSize / 10` becomes zero for event-loop construction, behavior depends on Netty constructors and config assumptions. TLS setup exceptions are logged but do not abort server construction, which can matter in secure deployments. `start` maps bind failures by inspecting the IOException message for `"Failed to bind to address"`. `stop` waits only five seconds for executors/server shutdown.

## Test Signals

Tests should verify random and fixed port assignment, datanode port registration, TLS-enabled builder behavior, submitRequest error translation, pipeline report identity, bind failure mapping to `BindException`, executor shutdown interrupt handling, and epoll/NIO branch configuration where practical.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerGrpc.java -->
