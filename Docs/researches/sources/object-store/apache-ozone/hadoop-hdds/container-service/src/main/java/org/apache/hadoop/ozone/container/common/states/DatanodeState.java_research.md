# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/DatanodeState.java

## Purpose
`DatanodeState<T>` is the lifecycle interface for executable datanode state tasks.

## Important APIs and Types
Implementations must define `onEnter()`, `onExit()`, `execute(ExecutorService)`, and `await(long, TimeUnit)`. The generic return type `T` is the next state type, used by datanode tasks as `DatanodeStateMachine.DatanodeStates`. `clear()` is a default no-op cleanup hook.

## Control Flow
`StateContext.execute()` obtains the current task, calls `onEnter()` when entering a state, calls `execute()` with the state-machine executor, waits through `await()`, runs `onExit()` on state transition, sets the new state, and finally invokes `clear()`.

## State and Persistence Behavior
The interface stores no state. Implementations may hold futures or resources and may trigger persistence, such as `InitDatanodeState` writing datanode details.

## Dependencies and Integration Points
It integrates `StateContext` with concrete datanode states under `states.datanode` and uses Java executor/future timeout primitives.

## Risks
The interface notes `execute()` is unsafe to call concurrently; callers must serialize it. Implementations must handle `await()` timeout and cleanup correctly or the state machine can stall.

## Test Signals
Tests should exercise `StateContext.execute()` against fake implementations to verify lifecycle hook order, transition handling, timeout propagation, and `clear()` invocation.
