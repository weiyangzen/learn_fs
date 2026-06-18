# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/SetNodeOperationalStateCommandHandler.java

## Purpose
Handles SCM set-node-operational-state commands by persisting the datanode operational state and notifying services that depend on node state.

## Important APIs and Types
Implements `CommandHandler` for `setNodeOperationalStateCommand`. It stores configuration, a replication-supervisor state consumer, an optional disk-balancer state consumer, invocation count, and latency metric. Private helpers `persistUpdatedDatanodeDetails()` and `persistDatanodeDetails()` write the updated datanode ID file.

## Control Flow
`handle()` validates command type, extracts `SetNodeOperationalStateCommandProto`, copies the current `DatanodeDetails`, updates persisted operation state and expiry, writes it to the configured datanode ID file, updates the live `DatanodeDetails`, notifies disk balancer if present, notifies replication supervisor, and records latency.

## State and Persistence Behavior
This handler directly persists `DatanodeDetails` to the datanode ID file via `ContainerUtils.writeDatanodeDetailsTo()`. It also mutates the in-memory `DatanodeDetails` after a successful write.

## Dependencies and Integration Points
It integrates with `HddsServerUtil.getDatanodeIdFilePath()`, `ContainerUtils`, `ReplicationSupervisor.nodeStateUpdated`, optional disk balancer service, and SCM operational-state commands.

## Risks
Persistence failure is logged but not propagated, and service consumers are still notified after the catch block. The TODO notes duplicate persistence logic with `HddsDatanodeService` and `InitDatanodeState`. If write succeeds but later mutation or notification fails, state can diverge.

## Test Signals
Tests should verify file persistence, in-memory state update, expiry propagation, disk balancer optional callback, supervisor callback, wrong command type handling, and behavior when persistence throws.
