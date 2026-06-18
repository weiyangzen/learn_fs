# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/metrics/TestContainerMetrics.java

Purpose: This test verifies storage-container and per-volume I/O metrics for both standalone gRPC xceiver and Ratis xceiver paths. It sends create-container, write-chunk, and read-chunk commands through a real dispatcher and asserts operation counters, byte counters, percentile gauges, and volume I/O stats.

Important APIs and types: The suite uses `XceiverClientGrpc`, `XceiverClientRatis`, `XceiverServerGrpc`, `XceiverServerRatis`, `HddsDispatcher`, `ContainerMetrics`, `MutableVolumeSet`, `HddsVolume`, `VolumeChoosingPolicy`, `Handler.getHandlerForContainerType`, `ContainerChecksumTreeManager`, `StateContext`, `ContainerController`, `StorageVolumeUtil`, `DefaultMetricsSystem`, and metrics helpers `assertCounter`, `assertQuantileGauges`, and `getMetrics`.

Control flow: `setup` enables MiniCluster metrics mode, sets percentile intervals to one second, disables Ratis data stream, sets metadata dirs, and creates the volume choosing policy. Each test calls `runTestClientServer` with protocol-specific configuration, client, server, and server-init factories. The runner creates a single-node mock pipeline, creates a mutable volume set, starts the server with a dispatcher built from real key-value handlers, connects the client, writes a chunk to a test block, reads it back, and then asserts metrics. Cleanup removes registered `ContainerMetrics`, shuts down the volume set, closes the client, and stops the server.

State and persistence behavior: The test uses temporary datanode and Ratis storage dirs and sets each `HddsVolume` DB parent directory to a temp location. A real container is created implicitly by the write path, chunk bytes are written and read, and volume I/O statistics record the actual 1024-byte operations. Cleanup deletes configured datanode and Ratis storage directories.

Dependencies and integration points: It covers xceiver transports, dispatcher-to-handler routing, key-value container operations, checksum tree manager wiring, volume selection, metrics system registration, and volume I/O metric sources.

Risks: The static `CONF` is mutated across protocol modes, so cleanup is important. Metric names and percentile interval suffixes are string-sensitive. The test sleeps to let quantile gauges roll to the configured interval.

Test signals: Expected metrics are `NumOps == 3`, one create container, one write chunk, one read chunk, 1024 bytes written and read, write-chunk quantile gauges for the one-second interval, and volume I/O counters showing 1024 read bytes, one read op, 1024 write bytes, and one write op.
