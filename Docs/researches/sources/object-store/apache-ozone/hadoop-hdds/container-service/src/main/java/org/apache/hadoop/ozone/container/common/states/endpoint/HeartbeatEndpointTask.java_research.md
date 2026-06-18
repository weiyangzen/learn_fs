<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/HeartbeatEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/HeartbeatEndpointTask.java

## Purpose

`HeartbeatEndpointTask` builds and sends a datanode heartbeat to an SCM endpoint, attaches queued reports/actions, and converts SCM heartbeat responses into datanode command queue work. It is the steady-state endpoint task for `EndpointStateMachine.EndPointStates.HEARTBEAT`. The complete 534-line file was read.

## Important APIs, Types, and Functions

The class implements `Callable<EndpointStateMachine.EndPointStates>`. Public construction is through `newBuilder()` and `Builder` setters for endpoint, config, datanode details, context, and optional layout version manager. `call()` is the main entry point. Helper methods include `addReports`, `addContainerActions`, `addPipelineActions`, `addQueuedCommandCounts`, `processResponse`, `processCommonCommand`, `processReregisterCommand`, and `putBackIncrementalReports`.

## Control Flow

`call` locks the endpoint, checks that datanode details were set, builds `SCMHeartbeatRequestProto` with datanode identity and layout version, then adds all currently available reports from `StateContext`, pending container and pipeline actions up to configured limits, and queued SCM command counts. It sends the heartbeat through `rpcEndpoint.getEndPoint().sendHeartbeat`. A successful response is validated against the datanode UUID, updates leader SCM term when present, decodes each SCM command by type, and enqueues command objects into `StateContext`. A `reregisterCommand` moves the endpoint back to GETVERSION and triggers an immediate heartbeat cycle. `IOException` does not drop incremental data: command status and incremental container reports are put back into context for retry.

## State and Persistence Behavior

The task keeps only per-call request state and configured max action counts. Heartbeat side effects are on `EndpointStateMachine` last-success/missed counters, `StateContext` report/action/command queues, SCM term tracking, and parent heartbeat timing. It does not write persistent storage directly.

## Dependencies and Integration Points

Dependencies include SCM datanode protocol protobufs, `HDDSLayoutVersionManager`, `StateContext`, datanode details, many `SCMCommand` subclasses, and configuration keys `HDDS_CONTAINER_ACTION_MAX_LIMIT` and `HDDS_PIPELINE_ACTION_MAX_LIMIT`. It integrates with report producers through `StateContext.getAllAvailableReports(address)` and with command executors through `context.addCommand`.

## Risks and Edge Cases

`addReports` uses protobuf descriptor full names to match arbitrary report messages to heartbeat fields, so schema changes require care. Unknown command types throw `IllegalArgumentException`, which can fail the task. Incremental report retry covers only command status and incremental container reports; cumulative reports are intentionally not put back. Builder validation misses a null `context` check even though the constructor and call path require it. Response UUID mismatch is a hard precondition failure.

## Test Signals

Tests should verify report descriptor placement, action limit behavior, queue-count serialization, command decoding for every switch branch, reregister state transition and immediate heartbeat trigger, incremental report put-back on IOException, term/token/deadline propagation to commands, and failure behavior for mismatched UUID or unknown command type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/HeartbeatEndpointTask.java -->
