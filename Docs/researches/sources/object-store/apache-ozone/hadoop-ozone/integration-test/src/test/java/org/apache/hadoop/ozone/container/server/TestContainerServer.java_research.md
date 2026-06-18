# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestContainerServer.java

Purpose: Smoke and integration tests for unsecured container xceiver servers over standalone gRPC and Ratis gRPC transports. It verifies client/server wiring with a trivial dispatcher and with a real `HddsDispatcher` stack.

Important APIs, types, and functions: The file uses `XceiverServerGrpc`, `XceiverServerRatis`, `XceiverClientGrpc`, `XceiverClientRatis`, `MockPipeline`, `RatisTestHelper`, `HddsDispatcher`, `ContainerController`, `Handler.getHandlerForContainerType`, `MutableVolumeSet`, `ContainerMetrics`, and `DNCertificateClient`. Core helpers are `runTestClientServer`, `runTestClientServerRatis`, `newXceiverServerRatis`, `createDispatcher`, and the inner `TestContainerDispatcher`.

Control flow: Static setup enables mini-cluster metrics, prepares metadata paths, disables Ratis datastream, and creates a datanode certificate client. `testClientServer` configures the standalone container IPC port from the mock pipeline, starts `XceiverServerGrpc` with a test dispatcher, connects a gRPC client, and sends a create-container request. `testClientServerRatisGrpc` runs the same pattern for 1-node and 3-node Ratis pipelines. `testClientServerWithContainerDispatcher` builds a full dispatcher with container set, volume set, handlers, and metrics, then verifies a create request through gRPC.

State and persistence behavior: Server tests create temporary datanode metadata and volume roots. The full dispatcher constructs actual handlers and volume sets and sets an SCM cluster ID, so create-container can touch persistent container metadata. The simple dispatcher returns a synthetic create-container response without storing container state.

Dependencies and integration points: Covers client/server transport constructors, Ratis server initialization, handler registration for container types, local datanode volume setup, metrics system, and xceiver command request tracing.

Risks: Uses a shared static `OzoneConfiguration`, so mutations across subtests must not conflict. Temporary Ratis storage paths are derived from datanode IDs. The simple dispatcher only validates transport plumbing, not container semantics. Full dispatcher setup must stay in sync with handler constructor requirements.

Test signals: Requests must carry a trace ID; clients must connect and send a create-container command without exception. Resource cleanup closes the client and stops all servers.
