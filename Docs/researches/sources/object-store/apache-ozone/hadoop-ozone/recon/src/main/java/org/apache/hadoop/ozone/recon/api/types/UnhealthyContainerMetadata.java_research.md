# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/UnhealthyContainerMetadata.java

## Purpose
DTO for unhealthy container rows, converting database records into API output with state, unhealthy-since time, expected/actual/delta replica counts, reason, key count, pipeline UUID, and replica history.

## Important APIs, Types, And Functions
declares `UnhealthyContainerMetadata`; key fields include `containerID`, `containerState`, `unhealthySince`, `expectedReplicaCount`, `actualReplicaCount`, `replicaDeltaCount`, `reason`, `keys`, `pipelineID`, `replicas`; important methods include `getContainerID`, `getKeys`, `getReplicas`, `getContainerState`, `getExpectedReplicaCount`, `getActualReplicaCount`, `getReplicaDeltaCount`, `getReason`, `getUnhealthySince`, `getPipelineID`.

## Control Flow
The record constructor copies fields from generated `UnhealthyContainers` POJOs and attaches replica history supplied by callers.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover each unhealthy state, replica delta values, reason propagation, and replica history serialization.
