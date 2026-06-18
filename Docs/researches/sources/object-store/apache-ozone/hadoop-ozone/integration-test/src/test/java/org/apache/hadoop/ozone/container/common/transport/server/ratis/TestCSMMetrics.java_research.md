# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestCSMMetrics.java

Purpose: This test validates metrics emitted by the Ratis `ContainerStateMachine` around write, apply, commit, and read/query operations. It uses a lightweight Ratis server with a test dispatcher to check metric counters and latency gauges before and after container protocol commands.

Important APIs and types: The file uses `CSMMetrics`, `XceiverServerRatis`, `XceiverClientRatis`, `RatisTestHelper`, `MockPipeline`, `Pipeline`, `RaftGroupId`, `ContainerDispatcher`, `ContainerController`, `ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `ContainerTestHelper`, and metrics helpers `getMetrics`, `assertCounter`, and `getDoubleGauge`.

Control flow: `testContainerStateMachineMetrics` delegates to `runContainerStateMachineMetrics` with gRPC Ratis initialization and server/client factories. The runner creates a mock pipeline, configures Ratis, starts one xceiver server per pipeline node, initializes the Ratis group, connects a client, asserts initial CSM counters and latency gauges are zero, sends a write-chunk request, checks write/apply/commit/bytes counters and latency gauges advanced, then sends a read-chunk request and checks query counter growth. A `finally` block closes the client and stops all servers.

State and persistence behavior: The test uses temporary Ratis storage directories under `@TempDir` and a new empty `ContainerSet` controlled by `ContainerController`. The dispatcher returns create-container-style success responses rather than real key-value persistence, so metrics state is the primary state under test. Ratis state machine metrics are keyed by `CSMMetrics.SOURCE_NAME + RaftGroupId`.

Dependencies and integration points: Coverage sits at the transport/state-machine layer: xceiver client, Ratis server, Raft group initialization, container state machine metrics source registration, and command dispatch. The custom dispatcher isolates metrics from real container storage behavior.

Risks: Because `TestContainerDispatcher` does not perform real storage operations, it validates state-machine metric accounting rather than full container command semantics. Metric names are string-sensitive and can break on metric renames.

Test signals: Strong signals are zero initial counters and gauges, one write state-machine op, one apply transaction, 1024 written and committed bytes, zero verify failures, positive write/apply latency gauges after write chunk, and one query state-machine op after read chunk.
