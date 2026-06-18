<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientMetrics.java

Purpose: Verifies `XceiverClientMetrics` counters for synchronous latency and asynchronous pending operations.

Important APIs and types: Uses `MiniOzoneCluster`, `XceiverClientManager`, `XceiverClientSpi`, `ContainerTestHelper`, `ContainerCommandRequestProto`, `CompletableFuture<ContainerCommandResponseProto>`, metrics helpers `getMetrics`, `assertCounter`, and `getLongCounter`. The test is marked flaky for HDDS-11646.

Control flow: The test allocates one container, acquires a client, sends a synchronous create-container request, and checks zero pending counters plus a create latency operation count. It then starts a sender thread that repeatedly issues ten async write-small-file requests, waits until pending metrics become positive, stops the thread, waits for all futures, and checks pending counters return to zero.

State and persistence behavior: The MiniOzoneCluster persists allocated container state and datanode writes. Runtime state includes the metrics source, outstanding async response futures, `breakFlag`, and a latch that coordinates the sender thread shutdown.

Dependencies and integration points: Integrates live xceiver transport, SCM allocation, datanode command execution, Hadoop metrics2, and Ozone test metrics assertions.

Risks: This is timing-sensitive and explicitly flaky. Pending counters may be transient if async requests complete before metrics sampling. The sender thread catches and ignores exceptions, so the wait condition is the main failure detector.

Test signals: Strong signals are `PendingOps` and `numPendingCreateContainer` at zero after sync command, `CreateContainerLatencyNumOps` incremented to one, positive `PendingOps` and `numPendingPutSmallFile` during async load, all futures completed, and pending counters returning to zero.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientMetrics.java -->
