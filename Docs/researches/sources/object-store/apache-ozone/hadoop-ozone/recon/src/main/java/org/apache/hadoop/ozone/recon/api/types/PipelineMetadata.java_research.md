# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/PipelineMetadata.java

## Purpose
Detailed pipeline DTO for Recon pipeline APIs, including ID, state, leader, datanodes, leader election metrics, replication config, duration, and container count.

## Important APIs, Types, And Functions
declares `PipelineMetadata`, `Builder`; key fields include `pipelineId`, `status`, `leaderNode`, `datanodes`, `lastLeaderElection`, `duration`, `leaderElections`, `replicationType`, `replicationFactor`, `containers`; important methods include `getPipelineId`, `getStatus`, `getLeaderNode`, `getDatanodes`, `getLastLeaderElection`, `getDuration`, `getLeaderElections`, `getReplicationType`, `getReplicationFactor`, `getContainers`, `newBuilder`, `build`.

## Control Flow
Builder defaults leader/duration/election/container fields, requires pipeline id, status, datanodes, and replication type, and derives replication strings from `ReplicationConfig`.

## State And Persistence Behavior
The class does not own durable persistence; it represents data read from or written by Recon services, OM metadata tables, SCM state, or HTTP/LLM integration at the API boundary.

## Dependencies And Integration Points
Integrates with JAXB/XML, HDDS replication, SCM pipeline metadata. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover required-field validation, Ratis and EC replication strings, and absent leader handling.
