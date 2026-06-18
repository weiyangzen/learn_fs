<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/SCMEvents.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/SCMEvents.java

## Purpose

`SCMEvents` is the namespace of typed events used by SCM subsystems to communicate through the HDDS event queue. It centralizes event names and payload types for reports, datanode commands, pipeline actions, node state changes, replication notifications, and state-machine readiness.

## Important APIs, Types, and Functions

The class exposes static `TypedEvent` and `Event` constants including `NODE_REPORT`, `DATANODE_COMMAND_COUNT_UPDATED`, `NODE_REGISTRATION_CONT_REPORT`, `CONTAINER_REPORT`, `INCREMENTAL_CONTAINER_REPORT`, `CONTAINER_ACTIONS`, `PIPELINE_REPORT`, `OPEN_PIPELINE`, `PIPELINE_ACTIONS`, `CMD_STATUS_REPORT`, `DATANODE_COMMAND`, `RETRIABLE_DATANODE_COMMAND`, `CLOSE_CONTAINER`, node health/admin events, `DELETE_BLOCK_STATUS`, `REPLICATION_MANAGER_NOTIFY`, `RECONCILE_CONTAINER`, and `STATEMACHINE_READY`.

## Control Flow

There is no executable flow beyond static event construction. Producers fire these constants into the event queue; listeners subscribe elsewhere based on the typed payload.

## State and Persistence Behavior

State is static event identity and event names. No persistence occurs. Event payloads are transient runtime messages.

## Dependencies and Integration Points

It integrates SCMDatanode heartbeat dispatchers, NodeManager, PipelineManager, ReplicationManager, command status handlers, safe mode rules, close-container workflows, Ratis state-machine readiness, and datanode command dispatch.

## Risks and Edge Cases

Event names and payload types form an internal compatibility contract. Changing a constant type or name can break listener registration. Some events use raw `Event<CommandForDatanode>` while most are `TypedEvent`.

## Test Signals

Tests should verify event queue wiring for each major producer/listener path, especially report dispatch, close-container events, retryable datanode commands, replication notifications, and state-machine ready events.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/events/SCMEvents.java -->
