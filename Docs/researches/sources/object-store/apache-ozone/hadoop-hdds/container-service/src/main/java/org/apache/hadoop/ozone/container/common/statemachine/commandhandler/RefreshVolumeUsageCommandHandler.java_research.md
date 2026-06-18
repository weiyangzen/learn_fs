# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/RefreshVolumeUsageCommandHandler.java

## Purpose
Handles SCM refresh-volume-usage commands by forcing all datanode volumes to refresh usage accounting.

## Important APIs and Types
Implements `CommandHandler` for `refreshVolumeUsageInfo`. It keeps invocation count and latency metrics. `handle()` calls `container.getVolumeSet().refreshAllVolumeUsage()`.

## Control Flow
The handler runs synchronously in the command processor thread. It logs receipt, increments invocation count, refreshes all volume usage, and records elapsed time.

## State and Persistence Behavior
It does not persist data directly. It refreshes in-memory or cached usage information in the volume set, which affects subsequent reports and volume selection.

## Dependencies and Integration Points
It depends on `OzoneContainer.getVolumeSet()` and the volume-set implementation. It participates in command-handler and queue metrics with zero internal queue.

## Risks
Synchronous refresh could delay command processing if volume usage scanning is slow. Exceptions are not caught locally, but `CommandDispatcher` catches handler exceptions and logs them.

## Test Signals
Tests should verify command type, invocation count, `refreshAllVolumeUsage()` call, latency metric update, and dispatcher-level exception handling for volume-set failures.
