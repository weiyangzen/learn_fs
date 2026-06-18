# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestOpenContainerCount.java

## Purpose
Tests that `NodeEndpoint.getDatanodes` reports the open-container count for a datanode and that the count decreases as containers move from `OPEN` to `CLOSED`.

## Important APIs, Types, And Functions
The test drives `NodeEndpoint`, `ReconStorageContainerManagerFacade`, Recon datanode protocol registration, heartbeat handling, `ContainerReportsProto`, `PipelineReportsProto`, `ContainerWithPipeline`, `ContainerInfo`, `DatanodesResponse`, and `DatanodeMetadata`. Helpers `initializeInjector`, `closeContainer`, `updateContainerReport`, and `waitAndCheckConditionAfterHeartbeat` build and mutate the SCM-side fixture.

## Control Flow
The injector initializes a Recon OM, two pipelines for one datanode, and ten open containers split across those pipelines. `setUp` registers the datanode with storage, container, and pipeline reports and processes the SCM event queue. The test waits until `NodeEndpoint` observes 10 containers and 2 pipelines, then closes containers one by one, updates mocked `StorageContainerServiceProvider` responses and the container report, re-registers the datanode, processes events, and asserts that `getOpenContainers` decrements each time.

## State And Persistence
Temporary Recon SQL, OM, and container DB state is created through `ReconTestInjector`. Runtime state is primarily SCM in-memory state plus mocked service-provider responses for `getContainerWithPipeline` and `getExistContainerWithPipelinesInBatch`. The mutable `ContainerReportsProto.Builder` and `cpw` list are the local sources of truth for each close transition.

## Dependencies And Integration Points
The test integrates datanode registration, heartbeat/container report processing, Recon pipeline management, SCM container lookup, and the Node REST endpoint. It mocks HTTP calls and Recon node details through `ReconUtils`, but uses the real Recon facade event processing path.

## Risks
The test is asynchronous and uses `LambdaTestUtils.await`, so event queue timing and processing delays are possible flake points. It assumes one datanode and exact container ordering by ID in the report builder. If NodeEndpoint changes container-count semantics to count only reported replicas, only SCM containers, or only pipelines known before report processing, this test will expose the behavior change.

## Test Signals
The main signal is an initial datanode metadata row with 10 containers, 2 pipelines, and 10 open containers followed by a deterministic decrement to zero as each container is marked closed.
