# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulationState.java

## Purpose
Mutable state model for one simulated datanode used by Vapor’s SCM/Recon stress simulator.

## Important APIs, types, and functions
Tracks `DatanodeDetails`, registration flag, endpoint-specific report state, pipelines, containers, readonly flag, full-container-report interval, and target container count. Builds heartbeat, node report, pipeline report, full container report, and incremental container reports. Includes Jackson serializers for `DatanodeDetails`.

## Control flow
`ackHeartbeatResponse` applies SCM commands: create pipeline unless readonly, close pipeline, and close container. `heartbeatRequest` builds a datanode heartbeat with node/pipeline reports and either a full report when due or pending ICRs. `newContainer` and `closeContainer` mutate container state and enqueue ICRs for every endpoint.

## State and persistence behavior
State is serialized to JSON by `DatanodeSimulator`, including datanode details, pipelines, containers, FCR duration, and target count. Endpoint ICR scheduling is runtime-only and reinitialized after reload.

## Dependencies and integration points
Uses HDDS protocol protobufs, container replica states, storage location reports, Jackson binary serialization for datanode details, and SCM command types.

## Risks and edge cases
Most methods synchronize except readonly setter. Report data uses synthetic fixed metrics. Full-report scheduling uses random initial delay to avoid spikes. Unknown close-container commands only log errors.

## Test signals
No direct tests. Observable signals are heartbeat contents, FCR/ICR counts, pipeline set mutations, and JSON reload compatibility.
