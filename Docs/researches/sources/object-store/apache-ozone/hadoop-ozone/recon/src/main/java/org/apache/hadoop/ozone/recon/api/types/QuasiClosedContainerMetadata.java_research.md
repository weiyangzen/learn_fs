# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/QuasiClosedContainerMetadata.java

## Purpose
DTO for quasi-closed container reports, including container/pipeline identity, key count, state-enter time, expected/actual replica counts, and replica history.

## Important APIs, Types, And Functions
declares `QuasiClosedContainerMetadata`; key fields include `containerID`, `pipelineID`, `keys`, `stateEnterTime`, `expectedReplicaCount`, `actualReplicaCount`, `replicas`; important methods include `getContainerID`, `setContainerID`, `getPipelineID`, `setPipelineID`, `getKeys`, `setKeys`, `getStateEnterTime`, `setStateEnterTime`, `getExpectedReplicaCount`, `setExpectedReplicaCount`, `getActualReplicaCount`, `setActualReplicaCount`.

## Control Flow
Mutable bean with Jackson properties used by quasi-closed container endpoints.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover replica-count deltas at producing service level and JSON property names.
