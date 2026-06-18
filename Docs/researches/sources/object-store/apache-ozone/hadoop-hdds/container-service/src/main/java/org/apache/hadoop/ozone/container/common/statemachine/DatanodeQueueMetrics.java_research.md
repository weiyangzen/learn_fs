# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/DatanodeQueueMetrics.java

## Purpose
`DatanodeQueueMetrics` publishes Hadoop metrics for datanode queue depths: pending SCM commands in `StateContext`, queued commands inside registered handlers, incremental report queues, container action queues, and pipeline action queues per endpoint.

## Important APIs and Types
The class is a singleton `MetricsSource` registered as `DatanodeQueueMetrics`. `create(DatanodeStateMachine)` registers it with `DefaultMetricsSystem`; `unRegister()` clears and unregisters it. `getMetrics()` emits gauges using `MetricsRecordBuilder`. Endpoint-aware maps are maintained by `addEndpoint()` and `removeEndpoint()`.

## Control Flow
Construction initializes metrics names for every `SCMCommandProto.Type` in both state-context and dispatcher namespaces. On each scrape, it asks `StateContext.getCommandQueueSummary()`, `CommandDispatcher.getQueuedCommandCount()`, and endpoint queue-size maps on the context, then emits gauges.

## State and Persistence Behavior
State is process-local metrics metadata and the static singleton. No durable state is written. Endpoint maps must track `StateContext.addEndpoint/removeEndpoint` or stale gauges can remain.

## Dependencies and Integration Points
It integrates with Hadoop metrics2, `EnumCounters`, and `DatanodeStateMachine`. `StateContext` calls `addEndpoint()` and `removeEndpoint()` when endpoints change. `DatanodeStateMachine.close()` unregisters it.

## Risks
The singleton can return an existing instance for a different state machine in tests or embedded deployments if not unregistered. Metric names are generated from host names and command names; unusual host strings may create awkward metric identifiers. Concurrent endpoint changes are not explicitly synchronized inside this class.

## Test Signals
Tests should assert singleton lifecycle, endpoint map growth and shrink, queue gauge values for both context and dispatcher queues, and clean unregister behavior during datanode shutdown.
