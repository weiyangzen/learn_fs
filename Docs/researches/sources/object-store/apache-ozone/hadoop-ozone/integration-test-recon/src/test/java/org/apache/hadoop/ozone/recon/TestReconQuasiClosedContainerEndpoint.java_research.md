# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconQuasiClosedContainerEndpoint.java

## Purpose

This integration test validates the Recon `GET /containers/quasiClosed` endpoint through direct `ContainerEndpoint` calls. It checks basic listing, pagination, count-only behavior for `limit=0`, and bad-request handling for invalid parameters.

## Important APIs, types, and functions

The test uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `ContainerEndpoint`, `QuasiClosedContainersResponse`, `QuasiClosedContainerMetadata`, `ContainerInfo`, and `ContainerWithPipeline`. The key helper is `createQuasiClosedContainer()`, which injects containers directly into Recon's container manager and applies `FINALIZE` and `QUASI_CLOSE` lifecycle events.

## Control flow, state, and persistence

The cluster is started once per class with three datanodes. After Recon pipeline state is available, tests create artificial container IDs from an `AtomicLong` starting at 10000 so each test can page from its own cursor. The containers are not created in SCM or on datanodes; they are in-memory Recon state only. Pagination walks `getQuasiClosedContainers(pageSize, cursor)` and updates the cursor from `lastKey`.

## Dependencies and integration points

The file isolates endpoint behavior from container health and metadata managers by constructing `ContainerEndpoint` with only the Recon SCM facade and nulls for unused collaborators. It depends on at least one RF3 pipeline being present in Recon to attach to injected containers.

## Risks and test signals

Because it mutates shared Recon state across class-level tests, the cursor strategy is critical to avoid cross-test contamination. Direct injection bypasses SCM sync and datanode reports, so it tests endpoint filtering/pagination rather than full ingestion. Passing signals include returned IDs containing created quasi-closed containers, expected replica count of 3, valid pipeline IDs and state-enter times, exactly four pages for 25 containers at page size 7, nonzero count with empty result for `limit=0`, and HTTP 400 for negative inputs.
