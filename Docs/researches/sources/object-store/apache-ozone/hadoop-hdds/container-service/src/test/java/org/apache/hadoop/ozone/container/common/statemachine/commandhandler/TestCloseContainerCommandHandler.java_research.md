# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerCommandHandler.java

## Purpose
`TestCloseContainerCommandHandler` verifies datanode handling of SCM close-container commands across pipeline presence, force-close flags, already-closed containers, missing containers, and handler thread-pool sizing.

## Important APIs, Types, And Functions
- `CloseContainerCommandHandler.handle`, `getQueuedCount`, and `getThreadPoolMaxPoolSize` are under test.
- `ContainerController.markContainerForClose` and `ContainerSet` supply container lookup and lifecycle management.
- `Handler.markContainerForClose`, `quasiCloseContainer`, and `closeContainer` are verified.
- `XceiverServerSpi.isExist` and `submitRequest` represent pipeline/Ratis write-channel integration.
- Helpers create close commands with known/unknown pipelines and force flags.

## Control Flow
Setup creates a `KeyValueContainer` bound to a random pipeline, adds it to `ContainerSet`, wires a `ContainerController` with a mocked handler, and configures the mocked write channel to recognize one pipeline and reject another. Tests submit close commands, wait until the handler queue drains, and verify handler/write-channel side effects. With an existing pipeline, the container is marked closing and a close request is submitted to the write channel. Without a pipeline, it is marked and then quasi-closed. Force close without a pipeline closes directly; force close with an existing pipeline still submits through the pipeline and does not close locally immediately. Already closed containers are no-ops. Missing and explicitly missing containers throw `ContainerNotFoundException` when marking for close.

## State And Persistence Behavior
The file uses in-memory `ContainerSet` and container data state. It validates state transitions through mocked handler methods rather than real disk mutation. Queue state is observed through `getQueuedCount`.

## Dependencies And Integration Points
The test depends on Ozone command classes, `PipelineID`, `XceiverServerSpi`, `ContainerController`, `Handler`, `KeyValueContainer`, and container layout parameterization. It protects SCM command handling at the boundary between local container state and Ratis pipeline closure.

## Risks And Edge Cases
Covered risks include closing through a missing pipeline, force close semantics, quasi-closed force-close behavior, idempotent close of already closed containers, missing-container errors, and asynchronous queue completion. The difference between force-close with and without a live pipeline is a key semantic risk.

## Test Signals
Signals are Mockito method verifications, exception message containment, and queue-drain waits. Thread-pool size is asserted as 1.
