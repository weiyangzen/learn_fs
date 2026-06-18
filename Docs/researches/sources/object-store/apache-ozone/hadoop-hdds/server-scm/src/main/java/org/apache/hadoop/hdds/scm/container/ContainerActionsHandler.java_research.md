<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerActionsHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerActionsHandler.java

## Purpose
Routes action requests reported by datanodes to SCM events. Currently it handles datanode requests to close containers.

## Important APIs, Types, And Functions
`ContainerActionsHandler` implements `EventHandler<ContainerActionsFromDatanode>`. `onMessage` iterates protobuf `ContainerAction` entries, converts IDs to `ContainerID`, and fires `SCMEvents.CLOSE_CONTAINER` for `ContainerAction.Action.CLOSE`.

## Control Flow
For each reported action, the handler switches on the action enum. CLOSE logs a debug reason and publishes the container ID for the close handler. Unknown actions are logged as warnings and otherwise ignored.

## State And Persistence
The handler is stateless. It does not update container state directly; downstream close-container processing owns state changes and command dispatch.

## Dependencies And Integration Points
Depends on heartbeat dispatcher `ContainerActionsFromDatanode`, protobuf `ContainerAction`, `DatanodeDetails`, `SCMEvents.CLOSE_CONTAINER`, and the event publisher. It is a narrow bridge from datanode action reports to SCM event handling.

## Risks And Test Signals
Adding new container action types requires switch expansion. Tests should verify one close event per CLOSE action, invalid action warning/no-op behavior, and preservation of the reported container ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerActionsHandler.java -->
