# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/FinalizeNewLayoutVersionCommandHandler.java

## Purpose
Handles SCM finalization commands that tell the datanode to finalize a new layout version after an upgrade.

## Important APIs and Types
Implements `CommandHandler` for `finalizeNewLayoutVersionCommand`. It reads `FinalizeNewLayoutVersionCommandProto`, checks `DatanodeStateMachine.getLayoutVersionManager().getUpgradeState()`, and invokes `DatanodeStateMachine.finalizeUpgrade()` when finalization is required.

## Control Flow
The handler runs synchronously in the command processor thread. It increments invocation count, checks the boolean `finalizeNewLayoutVersion`, verifies the local upgrade state is `FINALIZATION_REQUIRED`, and calls finalization. Exceptions are logged and not rethrown.

## State and Persistence Behavior
Persistent effects are in the upgrade finalizer and layout-version storage. The handler itself only stores metrics.

## Dependencies and Integration Points
It integrates with datanode layout-version management, `DataNodeUpgradeFinalizer`, SCM upgrade protocol commands, and command-handler metrics.

## Risks
Because it is synchronous, slow finalization setup could delay other command dispatching. Exceptions only log, so SCM must continue sending finalization commands until state converges. Multiple commands are guarded by checking upgrade state.

## Test Signals
Tests should verify finalization is invoked only when the command flag is true and state is `FINALIZATION_REQUIRED`, idempotent repeated command behavior, exception logging, and metrics.
