# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/states/datanode/TestRunningDatanodeState.java

## Purpose
`TestRunningDatanodeState` verifies `RunningDatanodeState.await` timing behavior while endpoint tasks are still executing versus when completed endpoint tasks are available.

## Important APIs, Types, And Functions
- `RunningDatanodeState.await`, `setExecutorCompletionService`, and `setExecutingEndpointCount` are under test.
- `ExecutorCompletionService` supplies endpoint task completion events.
- `EndpointStateMachine.EndPointStates.SHUTDOWN` is used as the completed task result.

## Control Flow
The test creates a mocked `SCMConnectionManager` returning two endpoint state machines, injects a completion service backed by a fixed thread pool, submits two tasks blocked on a future, and sets executing endpoint count to the pool size. A first `await(500ms)` call should wait at least 500ms because no task completes. After completing the first future, it submits two already-completing shutdown tasks and calls `await(500ms)` again; this time it should return before 500ms.

## State And Persistence Behavior
State is in-memory execution count and completion-service queue state. There is no persistence.

## Dependencies And Integration Points
The test depends on endpoint state machines, SCM connection manager, Java futures/executors, and Hadoop `Time.monotonicNow`. It protects the running datanode state's scheduling loop behavior.

## Risks And Edge Cases
Covered risk is `await` always sleeping for the full timeout even when endpoint tasks complete, or returning too early while all tasks are blocked. Timing assertions are inherently sensitive but use broad 500ms boundaries.

## Test Signals
Signals are elapsed-time assertions before and after future completion.
