# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/CommandDispatcher.java

## Purpose
`CommandDispatcher` maps SCM command protobuf types to the datanode command handlers that implement them. It is the single dispatch point after commands leave `StateContext`.

## Important APIs and Types
The private constructor validates handler uniqueness and creates `CommandHandlerMetrics`. Public APIs include `handle(SCMCommand<?>)`, `stop()`, `getQueuedCommandCount()`, test accessors for selected handlers, `getClosePipelineCommandHandler()`, and the nested `Builder`.

## Control Flow
`DatanodeStateMachine` builds a dispatcher by adding handlers and setting container, context, and connection manager. `handle()` looks up the handler by `command.getType()`, increments command metrics, invokes the handler, and logs unknown commands or handler exceptions without rethrowing.

## State and Persistence Behavior
The dispatcher stores an in-memory handler map and metrics source. It does not persist data. `stop()` delegates shutdown to each handler and unregisters command-handler metrics.

## Dependencies and Integration Points
It depends on `CommandHandler`, `CommandHandlerMetrics`, `OzoneContainer`, `StateContext`, and `SCMConnectionManager`. It feeds `DatanodeQueueMetrics` through `getQueuedCommandCount()`.

## Risks
Unknown command types are dropped after logging. Handler exceptions are swallowed, so command-specific failure reporting must happen inside handlers. Duplicate handlers fail constructor build. Missing required builder fields fail with `Objects.requireNonNull`.

## Test Signals
Tests should assert duplicate handler rejection, unknown command logging, handler invocation by type, metrics increment, stop delegation, and queue counter aggregation for all registered handlers.
