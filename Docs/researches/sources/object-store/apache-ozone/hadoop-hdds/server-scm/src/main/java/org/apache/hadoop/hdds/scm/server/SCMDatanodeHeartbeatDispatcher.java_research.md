# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDatanodeHeartbeatDispatcher.java

Purpose: `SCMDatanodeHeartbeatDispatcher` translates a datanode heartbeat protobuf into SCM node-manager processing plus typed events for node, container, pipeline, action, and command-status reports.

Important APIs and types: The main method is `dispatch(SCMHeartbeatRequestProto)`. Nested payload wrappers include `ReportFromDatanode`, `NodeReportFromDatanode`, `CommandQueueReportFromDatanode`, `LayoutReportFromDatanode`, `ContainerReport`, `ContainerReportType`, `ContainerReportFromDatanode`, `IncrementalContainerReportFromDatanode`, `ContainerActionsFromDatanode`, `PipelineReportFromDatanode`, `PipelineActionsFromDatanode`, and `CommandStatusReportFromDatanode`.

Control flow: `dispatch` converts datanode details from protobuf. If the node is unregistered, it queues a `ReregisterCommand` and returns that node's command queue without processing reports. For registered nodes, it fills a backward-compatible initial layout version if missing, processes layout and heartbeat command-queue reports through `NodeManager`, then fires events for optional node report, full container report, each incremental container report, container actions, pipeline reports/actions, and command status reports.

State and persistence behavior: The dispatcher owns no durable state. Event payloads carry datanode identity and protobuf report data. `IncrementalContainerReportFromDatanode.mergeReport` can combine report lists in memory for queue coalescing.

Dependencies and integration points: It is used by `SCMDatanodeProtocolServer.sendHeartbeat` and integrates with `NodeManager`, `EventPublisher`, `SCMEvents`, layout upgrade handling, and Ozone command generation.

Risks: Unregistered nodes do not have their reports processed, so registration state accuracy is critical. Layout-version fallback preserves older datanode compatibility but can mask missing layout reports. Event ordering follows the method order and downstream handlers may depend on it.

Test signals: Tests should cover unregistered reregister behavior, registered command returns, layout fallback, event firing for every heartbeat sub-report, ICR multiple-event behavior, command-status events, and ICR merge semantics.
