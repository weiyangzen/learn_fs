<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientGrpc.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientGrpc.java

Purpose: Verifies `XceiverClientGrpc` command-target selection, topology-aware read ordering, retry traversal across pipeline nodes, interruption handling, preference for in-service replicas, and connection reuse after `getBlock`.

Important APIs and types: The test builds `Pipeline` instances with `RatisReplicationConfig`, `PipelineID`, `DatanodeDetails`, `MockDatanodeDetails`, and ordered node lists. It exercises `XceiverClientGrpc.sendCommandAsync`, `XceiverClientSpi`, `XceiverClientReply`, and `ContainerProtocolCalls.getBlock`, `readChunk`, and `readSmallFile`. It toggles `OZONE_NETWORK_TOPOLOGY_AWARE_READ_KEY` and observes `NodeOperationalState`.

Control flow: `setup` creates three random datanodes and a closed three-node Ratis pipeline whose `nodesInOrder` list is reversed. Tests override `sendCommandAsync` in anonymous clients to record or fail requested datanodes. Helpers synthesize get-block, read-chunk, and read-small-file protocol calls and return a completed success response.

State and persistence behavior: No durable state is written. The meaningful state is the pipeline's node ordering, the client's remembered primary connection after a successful command, the current thread interrupt flag, and per-datanode operational state used to avoid maintenance nodes for primary reads.

Dependencies and integration points: Integrates the SCM pipeline model, Ozone network-topology read config, container protocol call helpers, protobuf container commands, and the xceiver client retry path. It is a focused unit-style integration test without a MiniOzoneCluster.

Risks: Several tests catch `IOException` and continue, so a command helper failure could be masked unless the final datanode set assertion detects it. Random maintenance-node selection can set the same node twice, but still asserts the first selected read target is in service. The connection reuse assertion depends on the current set of commands sharing the client's selected datanode.

Test signals: Key signals are `getClosestNode` versus `getFirstNode`, exactly one command target over repeated successful calls, all datanodes removed after repeated failures, `InterruptedIOException` preserving interrupt status and cause, first read target remaining `IN_SERVICE`, and only one seen datanode across get/read calls on one client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientGrpc.java -->
