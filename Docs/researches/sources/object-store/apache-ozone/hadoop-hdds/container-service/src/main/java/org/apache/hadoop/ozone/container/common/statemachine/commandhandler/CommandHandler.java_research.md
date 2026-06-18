# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandHandler.java

## Purpose
`CommandHandler` is the common interface for all datanode handlers of SCM commands.

## Important APIs and Types
Implementations must provide `handle()`, `getCommandType()`, invocation and latency metrics, and `getQueuedCount()`. Optional APIs include `stop()`, `getThreadPoolMaxPoolSize()`, and `getThreadPoolActivePoolSize()`. The default `updateCommandStatus()` updates command status in `StateContext` and logs if no entry exists.

## Control Flow
`CommandDispatcher` invokes `handle()` after selecting by `getCommandType()`. Async handlers use `getQueuedCount()` for queue metrics and override `stop()` to drain or stop internal executors.

## State and Persistence Behavior
The interface has no state. The default command-status helper mutates `StateContext.cmdStatusMap`, which is later reported back to SCM in command status reports.

## Dependencies and Integration Points
It ties handlers to `SCMCommandProto.Type`, `SCMCommand`, `OzoneContainer`, `StateContext`, and `SCMConnectionManager`. It also defines the metric contract consumed by `CommandHandlerMetrics` and `DatanodeQueueMetrics`.

## Risks
No return value or checked exception contract exists for `handle()`, so failures are usually logged and handled asynchronously. Implementations must keep metrics and queue counts consistent manually.

## Test Signals
Tests should validate the default status update helper, default thread-pool values, and that each concrete handler reports the command type it is registered under.
