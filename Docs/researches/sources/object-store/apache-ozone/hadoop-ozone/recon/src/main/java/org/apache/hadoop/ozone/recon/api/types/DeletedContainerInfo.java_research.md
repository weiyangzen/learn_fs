# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DeletedContainerInfo.java

## Purpose
DTO for deleted-container reports with container identity, pipeline, key count, state timestamps, used bytes, and replication details.

## Important APIs, Types, And Functions
declares `DeletedContainerInfo`; key fields include `containerID`, `pipelineID`, `numberOfKeys`, `containerState`, `stateEnterTime`, `lastUsed`, `usedBytes`, `replicationConfig`, `replicationFactor`; important methods include `getContainerID`, `getPipelineID`, `getNumberOfKeys`, `getContainerState`, `getStateEnterTime`, `getLastUsed`, `getUsedBytes`, `getReplicationConfig`, `getReplicationFactor`.

## Control Flow
Uses `JsonInclude` to omit default/empty values, so callers can return sparse rows without noisy zeros.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with Jackson, Jackson inclusion, HDDS replication, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover replication config/factor serialization, omitted defaults, and timestamp/unit consistency.
