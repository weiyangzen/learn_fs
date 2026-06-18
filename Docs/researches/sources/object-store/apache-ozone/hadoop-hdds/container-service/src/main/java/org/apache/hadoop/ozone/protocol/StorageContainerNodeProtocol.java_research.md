# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/StorageContainerNodeProtocol.java

Purpose: SCM-side node protocol abstraction for datanode state, registration, version exchange, heartbeat processing, and registration checks.

Important APIs and functions: `getVersion` returns a `VersionResponse` from an SCM version request. `register` accepts `DatanodeDetails`, node report, pipeline report, and layout version, returning a `RegisteredCommand`. `processHeartbeat` has a test-only default overload without queue report and the main overload with `CommandQueueReportProto`, returning a list of `SCMCommand`s. `isNodeRegistered` checks registration state.

Control flow and state: interface only. Implementations own node registry state, command queues, and heartbeat side effects.

Dependencies and integration: bridges datanode RPC/protobuf inputs to higher-level SCM command objects. The command queue report integrates with datanode-side supervisor queue metrics.

Risks and test signals: heartbeat command generation must be idempotent and registration-aware. Tests should cover unregistered nodes, queue report influence, version response content, layout-version registration, and default overload compatibility.
