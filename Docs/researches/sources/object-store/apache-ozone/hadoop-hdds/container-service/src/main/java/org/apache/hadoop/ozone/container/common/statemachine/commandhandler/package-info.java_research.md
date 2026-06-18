# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/package-info.java

## Purpose
Package documentation for `org.apache.hadoop.ozone.container.common.statemachine.commandhandler`.

## Important APIs and Types
The package contains `CommandHandler`, `CommandDispatcher`, and concrete SCM command handlers for close/delete container, close/create pipeline, delete blocks, replication, EC reconstruction, reconciliation, volume usage refresh, layout finalization, and node operational-state persistence.

## Control Flow
The package-level role is to receive commands drained from `StateContext` by `DatanodeStateMachine`, dispatch by protobuf command type, and either execute synchronously or enqueue work in specialized executors/supervisors.

## State and Persistence Behavior
Persistence is implemented by individual handlers, especially container state changes, block delete metadata, datanode ID file updates, and upgrade finalization. The package marker itself has no state.

## Dependencies and Integration Points
The package integrates the state machine with `OzoneContainer`, SCM protocol command wrappers, Ratis pipelines, replication supervisor, EC reconstruction coordinator, volume sets, and layout finalization.

## Risks
The package boundary contains both quick synchronous commands and resource-heavy async commands. Handler registration in `DatanodeStateMachine` must remain aligned with SCM command types.

## Test Signals
Package-level tests should focus on dispatcher coverage for every supported command type and handler-specific queue/metrics behavior.
