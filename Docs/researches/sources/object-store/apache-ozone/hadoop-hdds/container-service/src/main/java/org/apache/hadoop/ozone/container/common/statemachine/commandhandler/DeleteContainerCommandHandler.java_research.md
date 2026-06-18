# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteContainerCommandHandler.java

## Purpose
Handles SCM delete-container commands by scheduling container deletion on a bounded executor.

## Important APIs and Types
Implements `CommandHandler` for `deleteContainerCommand`. It tracks invocation count, timeout count, queue size, executor pool sizes, and latency. The protected constructor allows injecting a clock and executor for tests.

## Control Flow
`handle()` casts the command and submits `handleInternal()` to the executor. Rejected submissions are logged and dropped. `handleInternal()` checks the command deadline with the injected `Clock`, ignores stale SCM leader terms using `StateContext.getTermOfLeaderSCM()`, then calls `ContainerController.deleteContainer(containerID, force)`.

## State and Persistence Behavior
Container deletion and metadata/file cleanup are delegated to `ContainerController`. The handler only stores counters and metrics. Deadline expiration increments `timeoutCount`.

## Dependencies and Integration Points
It integrates with `OzoneContainer.getController()`, `DeleteContainerCommand`, `StateContext` leader-term tracking, and datanode configuration for thread and queue sizing.

## Risks
Rejected commands are logged but no command status is updated. Term filtering relies on the context term having been initialized. A command that waits too long is skipped so SCM can resend, which depends on SCM retry behavior. Force delete can remove containers in states that normal delete would reject at lower layers.

## Test Signals
Tests should cover deadline skip, stale-term skip, force flag propagation, rejection handling, queue and active pool metrics, timeout count, and graceful executor stop.
