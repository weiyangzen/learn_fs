# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/endpoint/TestHeartbeatEndpointTask.java

## Purpose
`TestHeartbeatEndpointTask` verifies datanode heartbeat request assembly and response command handling. It checks report inclusion, container actions, command queue reports, leader SCM term updates, and decoding of reconstruct/reconcile commands from SCM heartbeat responses.

## Important APIs, Types, And Functions
- `HeartbeatEndpointTask.call` sends heartbeat requests and processes responses.
- Builder API `HeartbeatEndpointTask.newBuilder` wires config, datanode details, `StateContext`, layout version manager, and endpoint state machine.
- `StateContext` supplies reports/actions and receives commands.
- `StorageContainerDatanodeProtocolClientSideTranslatorPB.sendHeartbeat` is mocked to capture requests and return responses.
- Protobufs under test include `SCMHeartbeatRequestProto`, `SCMHeartbeatResponseProto`, `NodeReportProto`, `ContainerReportsProto`, `CommandStatusReportsProto`, `ContainerAction`, and `CommandQueueReportProto`.
- Commands tested include `ReconstructECContainersCommand` and `ReconcileContainerCommand`.

## Control Flow
Command-response tests mock SCM to return a heartbeat response containing either reconstruct-EC or reconcile-container command protobufs. After `call`, the context command summary should include one command of the returned type. Request-assembly tests populate the context with no reports, node report, container report, command status report, container action, or all reports/actions. They capture the outgoing heartbeat and assert the corresponding optional fields and repeated counts are present or absent. The all-reports test also stubs queued command counts for every `SCMCommandProto.Type` and asserts the heartbeat contains a command queue report with matching types and counts. The no-report test also returns a newer SCM term and verifies `StateContext` updates its leader term.

## State And Persistence Behavior
State is the in-memory heartbeat context: report queues, command queues, container action queues, and leader SCM term. No data is persisted. Report retrieval may drain queues depending on report type.

## Dependencies And Integration Points
The test integrates heartbeat endpoint logic with SCM protocol translator, datanode details, layout version manager, `StateContext`, command queue counters, EC replication config, and container action protobufs. It is a key boundary test between datanode state and SCM heartbeat protocol.

## Risks And Edge Cases
Covered risks include missing reports in heartbeat requests, accidental inclusion of absent reports, command status/action omission, incorrect command queue report counts, failure to update SCM term, and failure to enqueue newly introduced reconstruct/reconcile commands. It does not cover network exceptions or endpoint state transitions after heartbeat failure.

## Test Signals
Signals include captured heartbeat field presence/count assertions, command queue summary counters, term equality, command queue report type/count matching, and command response decoding.
