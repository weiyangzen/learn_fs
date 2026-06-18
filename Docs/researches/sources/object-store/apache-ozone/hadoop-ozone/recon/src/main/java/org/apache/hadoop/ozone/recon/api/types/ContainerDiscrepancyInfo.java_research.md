# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ContainerDiscrepancyInfo.java

## Purpose
Represents Recon/SCM discrepancy details for a container, including key count, pipelines, and where the container exists.

## Important APIs, Types, And Functions
declares `ContainerDiscrepancyInfo`; key fields include `containerID`, `numberOfKeys`, `pipelines`, `existsAt`; important methods include `getContainerID`, `setContainerID`, `getNumberOfKeys`, `setNumberOfKeys`, `getPipelines`, `setPipelines`, `getExistsAt`, `setExistsAt`.

## Control Flow
Mutable bean populated by discrepancy scanners; `existsAt` is excluded from JSON when empty.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify pipeline serialization and empty `existsAt` omission for UI compatibility.
