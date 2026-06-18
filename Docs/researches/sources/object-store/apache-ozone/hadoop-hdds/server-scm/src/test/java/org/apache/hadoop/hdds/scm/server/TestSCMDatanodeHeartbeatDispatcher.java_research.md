# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMDatanodeHeartbeatDispatcher.java

Purpose: This unit test verifies how `SCMDatanodeHeartbeatDispatcher` converts datanode heartbeat protobuf fields into SCM events and how it reacts to heartbeats from unregistered datanodes after SCM restart. It protects the boundary between the datanode heartbeat RPC path, `NodeManager`, and the event bus.

Important APIs and types: The tests build `SCMHeartbeatRequestProto` messages carrying `NodeReportProto`, `ContainerReportsProto`, and `CommandStatusReportsProto`. They assert emitted events `NODE_REPORT`, `CONTAINER_REPORT`, and `CMD_STATUS_REPORT`, and payload wrapper types `NodeReportFromDatanode`, `ContainerReportFromDatanode`, and `CommandStatusReportFromDatanode`. The restart path verifies `NodeManager.addDatanodeCommand(DatanodeID, ReregisterCommand)`.

Control flow: Each dispatch test mocks `NodeManager.isNodeRegistered` as true, installs a small `EventPublisher`, builds one heartbeat, calls `dispatcher.dispatch`, and counts callbacks. The restart test leaves the registration check false by default, dispatches a heartbeat without reports, and verifies one re-register command is queued for the datanode ID.

State and persistence behavior: There is no durable state. Runtime state is limited to Mockito call history and an `AtomicInteger` event counter. The important state transition is the dispatcher deciding between report fan-out for registered nodes and re-registration command scheduling for unknown nodes.

Dependencies and integration points: This file integrates SCM heartbeat decoding with `NodeManager`, Ozone protocol command objects, generated datanode protocol protobufs, `MockDatanodeDetails`, and SCM's server event framework.

Risks: The tests only cover one command-status report and default report messages, not multiple command reports or malformed heartbeats. Event order is not asserted for the container/status case because the publisher only accepts either event. The unregistered-node case depends on Mockito's default false return for boolean methods.

Test signals: Strong signals are exact event counts, exact payload report identity, accepted event types, and the single `ReregisterCommand` enqueue when the node is not registered.
