# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ContainerEndpoint.java

## Purpose
`ContainerEndpoint` is the main Recon REST resource for container listing, key lookup by container, replica history, unhealthy/missing/quasi-closed container reporting, OM/SCM mismatch insights, deleted-container listing, and async unhealthy-container exports.

## Important APIs, Types, And Functions
The resource is `@Path("/containers")` and `@AdminOnly`. APIs include `GET /`, `/{id}/keys`, `/{id}/replicaHistory`, `/missing`, `/unhealthy`, `/unhealthy/{state}`, export job list/start/status/download/cancel paths, `/deleted`, `/mismatch`, `/mismatch/deleted`, and `/quasiClosed`. Helpers include `DataFilter`, `getUnhealthyContainersFromSchema`, `toUnhealthyMetadata`, `getBlocks`, and `toQuasiClosedMetadata`.

## Control Flow
Container listing pages from `ReconContainerManager`. Key lookup reads container-key prefixes, resolves `OmKeyInfo` from legacy or FSO tables, filters key-location versions, builds block metadata for the target container, and constructs full paths via namespace summaries. Unhealthy endpoints read SQL health rows, convert them to metadata with container info and replica history, and add summary counts. Mismatch endpoints merge sorted SCM container state and OM container metadata iterators to find containers missing in either side or deleted in SCM but present in OM. Export endpoints delegate queueing, progress, download limiting, streaming, and cancellation to `ExportJobManager`.

## State And Persistence
The endpoint reads SCM manager state, OM snapshot tables, Recon container-key metadata, namespace summary state, SQL unhealthy-container records, and export job files. It mutates export job state through submit/cancel/download reservation but does not modify container metadata.

## Dependencies And Integration Points
It integrates `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `PipelineManager`, `ReconContainerMetadataManager`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `ContainerHealthSchemaManager`, `ExportJobManager`, and numerous API DTOs.

## Risks
Some validation returns `406`, some `400`, and some methods coerce limits differently. `constructFullPath` can return empty during namespace rebuild. Export downloads reserve before streaming, so failed transfers still consume attempts. In-memory sorting/iteration over all SCM containers can be expensive for mismatch endpoints. The deprecated `/missing` path duplicates newer unhealthy-state behavior.

## Test Signals
Tests should cover pagination, negative input handling, key version/block mapping, missing namespace summaries, unhealthy state validation and summary counts, export queue and download limits, mismatch merge correctness for both filters, deleted-container filtering, quasi-closed pagination, and error mapping.
