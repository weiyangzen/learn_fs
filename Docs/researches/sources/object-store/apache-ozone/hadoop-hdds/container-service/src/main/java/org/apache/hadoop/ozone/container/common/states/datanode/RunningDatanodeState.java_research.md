<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/RunningDatanodeState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/RunningDatanodeState.java

## Purpose

`RunningDatanodeState` is the active datanode state that drives communication with SCM and passive endpoints such as Recon. It belongs to the datanode state-machine layer and is responsible for scheduling the endpoint-specific handshake/registration/heartbeat tasks while the datanode remains in the RUNNING state. The complete 235-line file was read for this report.

## Important APIs, Types, and Functions

The class implements `DatanodeState` and exposes `onEnter()`, `onExit()`, `execute(ExecutorService)`, `await(long, TimeUnit)`, and `clear()`. Its constructor receives `ConfigurationSource`, `SCMConnectionManager`, and `StateContext`. `buildEndPointTask(EndpointStateMachine)` maps endpoint states to `VersionEndpointTask`, `RegisterEndpointTask`, or `HeartbeatEndpointTask`. `computeNextContainerState(List<Future<EndPointStates>>)` converts endpoint task results into the next `DatanodeStateMachine.DatanodeStates`.

## Control Flow

`execute` builds an `ExecutorCompletionService`, scans the current endpoints from `SCMConnectionManager`, and submits one wrapper task per endpoint with a bounded wait against the endpoint's own executor. `GETVERSION` also forces the parent datanode's next heartbeat time to now so registration can follow immediately. `await` polls for the number of endpoint tasks that were actually submitted, bounded by the caller's timeout, then asks `computeNextContainerState` whether any endpoint returned `SHUTDOWN`. Timeout exceptions from endpoint work are logged as warnings and do not alone force datanode shutdown.

## State and Persistence Behavior

This class owns transient scheduler state only: `ecs` and `executingEndpointCount`. It does not persist data. Endpoint transitions are stored in `EndpointStateMachine`, while datanode-level state changes go through `StateContext`. The endpoint count is captured during `execute` because endpoint membership can change through reconfiguration before `await`.

## Dependencies and Integration Points

It integrates with `SCMConnectionManager`, `StateContext`, `DatanodeStateMachine`, `EndpointStateMachine`, and the three endpoint task classes in `states.endpoint`. It also depends on endpoint executor services, heartbeat/recon heartbeat frequencies in `StateContext`, and parent datanode container/details accessors.

## Risks and Edge Cases

If `buildEndPointTask` returns null, the code treats the endpoint as shutdown and moves the whole datanode toward shutdown. The wrapper computes `heartbeatFrequency` for passive endpoints but uses `context.getHeartbeatFrequency()` in the actual timeout, which is worth regression coverage if passive/recon timing semantics are important. Partial completion in `await` means late endpoint futures are ignored for that cycle. Interrupted waits restore interrupt status but still return RUNNING unless a collected result requested shutdown.

## Test Signals

Useful tests cover task selection for GETVERSION/REGISTER/HEARTBEAT, endpoint timeout logging without shutdown, shutdown propagation from any endpoint result, endpoint-count stability when connection manager membership changes, immediate heartbeat scheduling after GETVERSION/reregister, and passive endpoint timing expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/RunningDatanodeState.java -->
