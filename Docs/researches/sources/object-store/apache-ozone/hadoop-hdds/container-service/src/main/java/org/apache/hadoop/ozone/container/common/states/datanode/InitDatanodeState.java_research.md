# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/datanode/InitDatanodeState.java

## Purpose
`InitDatanodeState` performs datanode startup initialization for SCM and Recon connections, endpoint registration in `StateContext`, and datanode ID persistence.

## Important APIs and Types
It implements both `DatanodeState` and `Callable<DatanodeStateMachine.DatanodeStates>`. Key methods are `call()`, `persistContainerDatanodeDetails()`, `execute()`, and `await()`. It holds `SCMConnectionManager`, `ConfigurationSource`, `StateContext`, and the submitted future.

## Control Flow
`execute()` submits the instance to the state-machine executor. `call()` resolves SCM addresses from configuration, returns `SHUTDOWN` on invalid or empty address lists, postpones initialization by returning the current state when any SCM address is unresolved, adds SCM endpoints to the connection manager and context, optionally adds Recon, persists datanode details, and returns the next datanode state.

## State and Persistence Behavior
The state persists `DatanodeDetails` to the configured datanode ID file using `ContainerUtils.writeDatanodeDetailsTo()`. If persistence fails, it sets context state to `SHUTDOWN`. Endpoint state is added in both `SCMConnectionManager` and `StateContext`.

## Dependencies and Integration Points
It depends on `HddsServerUtil.getSCMAddressForDatanodes()`, `getReconAddressForDatanodes()`, datanode ID file config, `SCMConnectionManager`, and `StateContext`. It is selected by `StateContext.getTask()` when the datanode state is `INIT`.

## Risks
SCM endpoints are added before datanode ID persistence, so a persistence failure can leave endpoint resources created during shutdown. If adding an endpoint to the connection manager succeeds but context addition fails later, state can diverge. Unresolved SCM addresses postpone all initialization.

## Test Signals
Tests should cover invalid/empty SCM address shutdown, unresolved-address retry behavior, SCM and Recon endpoint additions, datanode ID file write success and failure, future submission/await, and next-state transition to `RUNNING`.
