# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteContainerCommandHandler.java

## Purpose
`TestDeleteContainerCommandHandler` verifies asynchronous delete-container command handling, deadline expiration, SCM leader-term filtering, and queue-size limiting.

## Important APIs, Types, And Functions
- `DeleteContainerCommandHandler.handle`, `getTimeoutCount`, and `getInvocationCount` are tested.
- `ContainerController.deleteContainer(containerId, force)` is the side effect under verification.
- `DeleteContainerCommand.setDeadline` and `setTerm` provide command metadata.
- `StateContext.getTermOfLeaderSCM` controls term acceptance.
- `TestClock` allows deterministic deadline advancement.

## Control Flow
Setup creates a test clock, mocked Ozone container/controller/context, and a default SCM term. The expiration test creates three commands, advances the clock so the first deadline is expired but the second is still valid and the third has no deadline, then verifies only valid/no-deadline commands reach the controller. Term tests execute a command only when its term matches the current leader term and drop it when the context has a newer term. Queue-size testing blocks the single worker with a lock, submits many duplicate commands with queue size one, and verifies only one delete reaches the controller while extra submissions are ignored/limited.

## State And Persistence Behavior
The handler tracks invocation and timeout counters plus executor queue state. Real container deletion persistence is mocked behind `ContainerController`.

## Dependencies And Integration Points
The test depends on Java executors/latches, Guava `ThreadFactoryBuilder`, Ozone `DeleteContainerCommand`, `StateContext`, and controller APIs. It protects command-handler integration with leader-term state and async worker queues.

## Risks And Edge Cases
Covered risks include executing expired SCM commands, accepting stale-term commands, unbounded queue growth, duplicate queued deletes, and deadline-free commands being dropped accidentally.

## Test Signals
Signals are controller invocation counts, timeout count, invocation count, and latch-based confirmation of async execution.
