# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerActionsHandler.java

## Purpose

This unit test verifies that `ContainerActionsHandler` translates datanode-reported container actions into SCM container events. It specifically covers a datanode `CLOSE` action caused by a full container.

## Important APIs, Types, and Functions

- `ContainerActionsHandler` handles `SCMEvents.CONTAINER_ACTIONS`.
- `CloseContainerEventHandler` is mocked as the downstream `SCMEvents.CLOSE_CONTAINER` handler.
- `ContainerActionsFromDatanode` wraps a datanode and `ContainerActionsProto`.
- `EventQueue.fireEvent` and `processAll` drive asynchronous handler execution.

## Control Flow and State Behavior

The test creates an `EventQueue`, registers the real actions handler and mocked close handler, builds a single `ContainerAction` with container ID 1, action `CLOSE`, and reason `CONTAINER_FULL`, then fires the container-actions event. After processing the queue, it verifies the close handler received `ContainerID.valueOf(1L)` once.

## State and Persistence

There is no persistence. State exists only in the event queue and generated protobuf action.

## Dependencies and Integration Points

The test integrates datanode heartbeat container-action payloads with SCM's internal event queue and close-container event handling.

## Risks and Test Signals

The key risk is losing or misrouting datanode close requests, causing full containers to remain open. The single verification provides a focused signal that close actions are converted to the expected SCM event.
