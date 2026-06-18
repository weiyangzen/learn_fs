# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeStateMachine.java

## Purpose
`DatanodeStateMachine` is the top-level container-service runtime coordinator. It constructs the datanode container stack, SCM connection manager, state context, command dispatcher, report manager, replication/reconstruction services, metrics, upgrade finalizer, and the daemon loops for heartbeats and command processing.

## Important APIs and Types
Key public APIs are `startDaemon()`, `stopDaemon()`, `close()`, `triggerHeartbeat()`, `join()`, `getQueuedCommandCount()`, `finalizeUpgrade()`, `queryUpgradeStatus()`, and accessors for context, container, dispatcher, supervisor, layout state, metrics, and executors. The nested `DatanodeStates` enum defines `INIT`, `RUNNING`, and `SHUTDOWN` with monotonic transition checks.

## Control Flow
The constructor wires all dependencies, creates bounded command-handler executors, registers command handlers, builds report publishers, and registers queue/netty metrics. `startDaemon()` creates a high-priority daemon thread running `startStateMachineThread()`. That loop initializes reports and the command processor, then repeatedly calls `StateContext.execute()` at heartbeat frequency. The command processor is a separate daemon that drains `StateContext.getNextCommand()` and invokes `CommandDispatcher.handle()`, sleeping until after the next heartbeat when idle.

## State and Persistence Behavior
The class owns lifecycle state via `StateContext`. It persists upgrade/layout state through `DatanodeLayoutStorage` and `DataNodeUpgradeFinalizer`, while container persistence is delegated to `OzoneContainer` and command handlers. Shutdown closes replication metrics, EC metrics, endpoint RPCs, the container, handlers, metrics, and executors.

## Dependencies and Integration Points
It integrates with `OzoneContainer`, `SCMConnectionManager`, `StateContext`, `ReportManager`, all command handlers, `ReplicationSupervisor`, pull/push replicators, EC reconstruction, certificate and secret-key clients, layout-version management, and reconfiguration.

## Risks
Constructor wiring has broad blast radius; missing a handler means SCM commands are logged as unknown. The command processor is single-threaded before dispatch, so a blocking synchronous handler can delay all commands. The uncaught exception handler for command processing restarts the thread, but repeated failures could spin. Shutdown ordering must avoid leaving async handlers or RPC endpoints alive.

## Test Signals
Tests should cover daemon start/stop, heartbeat triggering, `DatanodeStates` transition rules, handler registration, queue summary merging, executor resizing, constructor behavior under missing SCM address config, and shutdown cleanup of metrics and services.
