# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CloseContainerCommandHandler.java

## Purpose
Handles SCM close-container commands by moving local containers toward closed state, either through the write channel for active pipelines or directly/quasi-closed when the pipeline is absent.

## Important APIs and Types
Implements `CommandHandler` for `SCMCommandProto.Type.closeContainerCommand`. The constructor creates a bounded fixed `ThreadPoolExecutor`. `handle()` schedules async work, `getContainerCommandRequestProto()` builds an internal CloseContainer request, and metrics/queue/thread-pool accessors expose runtime behavior.

## Control Flow
`handle()` increments queued count and runs a task. The task fetches datanode details, casts `CloseContainerCommand`, gets the target container, calls `controller.markContainerForClose()`, then switches on container state. For `OPEN` or `CLOSING`, it submits a write-channel close request if the pipeline exists; otherwise force closes or quasi-closes. `QUASI_CLOSED` force commands close the container. `CLOSED` is a no-op, and unhealthy/invalid states are ignored.

## State and Persistence Behavior
Container state transitions are delegated to `ContainerController` and the write channel, which persist container metadata/state as appropriate. The handler itself stores invocation, queued count, executor, and latency metric only.

## Dependencies and Integration Points
It depends on `OzoneContainer`, `ContainerController`, `XceiverServerSpi` write channel, datanode details, tracing token propagation, and Ratis `NotLeaderException` handling.

## Risks
`CompletableFuture.runAsync` with a bounded executor can throw if the queue is full; unlike some handlers, this code does not catch `RejectedExecutionException` around submission. Force-close semantics differ sharply from quasi-close behavior. Missing containers are treated as informational rather than failure.

## Test Signals
Tests should verify state-dependent close behavior, encoded token propagation, NotLeader handling, missing container behavior, queue count decrement on completion, executor metrics, and rejection behavior when the queue is full.
