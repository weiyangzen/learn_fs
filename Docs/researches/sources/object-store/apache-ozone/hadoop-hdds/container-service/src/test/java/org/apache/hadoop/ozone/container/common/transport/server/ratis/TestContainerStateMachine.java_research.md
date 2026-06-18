# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/TestContainerStateMachine.java

## Purpose
Abstract JUnit 5 base for testing `ContainerStateMachine` behavior under both Ratis leader and follower modes. It verifies that failed writes and failed transaction application mark only the affected container unhealthy, prevent subsequent dispatches for that container, and propagate either thrown dispatcher failures or error responses as expected.

## Important APIs, Types, And Functions
`ContainerStateMachine.write` and `applyTransaction` are the primary behaviors. Mocked `ContainerDispatcher` returns runtime exceptions or failed `ContainerCommandResponseProto` values. `ContainerStateMachine.Context` supplies request/log protobufs, and helper methods build `WriteChunk` requests with specific container IDs. `ThrowableCatcher` captures async future failures.

## Control Flow
`setup()` builds mocked Ratis server/division/group/peer state and initializes the state machine with the subclass-provided leader flag. Tests run failing write/apply paths, verify dispatcher calls, retry affected and unaffected containers, and exercise a blocked dispatcher timeout.

## State And Persistence
No durable data is written. The meaningful state is in-memory failed-container tracking, async future completion, mocked log term/index, and request proto content. Two daemon executors are shared and shut down after all tests.

## Dependencies And Integration Points
Integrates Apache Ratis, Ozone container protobufs, dispatcher contexts, `StorageContainerException`, and `HDDS_CONTAINER_RATIS_STATEMACHINE_WRITE_WAIT_INTERVAL`. Concrete leader/follower subclasses execute the suite.

## Risks And Edge Cases
The timeout test depends on real sleep and interruption behavior. `testApplyTransactionFailure` is marked flaky. Exception wrapping differs between write and apply, so async implementation changes can affect assertions.

## Test Signals
Dispatcher invocation counts, captured future failures, `CONTAINER_INTERNAL_ERROR`, `CONTAINER_UNHEALTHY`, and a parsed successful apply response for a different container validate behavior.
