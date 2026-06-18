# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/DatanodePipeline.java

## Purpose
Compact pipeline descriptor embedded in datanode metadata, carrying pipeline UUID, replication type, replication factor string, and leader node.

## Important APIs, Types, And Functions
declares `DatanodePipeline`; key fields include `pipelineID`, `replicationType`, `replicationFactor`, `leaderNode`; important methods include `getPipelineID`, `getReplicationType`, `getReplicationFactor`, `getLeaderNode`.

## Control Flow
Constructed from a `ReplicationConfig`, turning type and replication into UI-friendly strings.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with HDDS replication, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover Ratis and EC replication string forms and nullable leader handling.
