# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestContainerPlacement.java

Purpose: integration-style test for capacity-based container placement using real SCM node/container manager wiring and synthetic node reports.

Important APIs and types: setup creates a temp metadata directory, `DBStore`, `SCMHAManagerStub`, `SequenceIdGenerator`, `MockNodeManager`, and `MockPipelineManager`. `createNodeManager()` builds `SCMNodeManager` with event handlers, network topology schemas, storage config, layout version manager, and empty SCM context. `createContainerManager()` spies the pipeline manager and stubs `checkSpaceAndRecordAllocation` true before constructing `ContainerManagerImpl`.

Control flow: `testContainerPlacementCapacity()` configures `SCMContainerPlacementCapacity`, registers four datanodes, pushes storage reports with capacity/used/remaining values, processes heartbeats, sleeps for asynchronous processing, checks aggregated node stats, allocates a Ratis container, manually adds replicas to the first replication-factor datanodes, and asserts the container manager sees the expected replica count.

State and persistence: uses a real RocksDB-backed `DBStore` under `@TempDir` for SCM metadata tables. It mutates node reports, node stats, pipeline/container state, and container replicas. Cleanup closes the DB store and SCM node/client resources.

Integration points and risks: exercises placement policy, node stats aggregation, pipeline allocation checks, and container state manager replica tracking. The explicit sleep is a flakiness risk; manual replica insertion bypasses datanode report flow; xceiver client is constructed but not central to assertions.
