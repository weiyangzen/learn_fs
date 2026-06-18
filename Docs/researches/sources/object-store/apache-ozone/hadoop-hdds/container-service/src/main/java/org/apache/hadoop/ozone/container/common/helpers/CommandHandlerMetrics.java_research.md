# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/CommandHandlerMetrics.java

## Purpose
Dynamic metrics source exposing per-SCM-command handler runtime, queue, pool, invocation, and received-command metrics.

## Important APIs, Types, And Functions
Static `create(handlerMap)` registers a metrics source. Public APIs are `increaseCommandCount`, `getMetrics`, and `unRegister`. Inner enum `CommandMetricsMetricsInfo` defines metric descriptions.

## Control Flow
At metrics collection time, it iterates the handler map and emits one record per command handler tagged by command type, reading total/average runtime, queued count, invocation count, optional pool sizes, and the locally tracked received command count.

## State And Persistence
In-memory state is the command handler map and an `AtomicInteger` count per command type. Metrics are exposed through `DefaultMetricsSystem`.

## Dependencies And Integration Points
Depends on SCM command protobuf `Type`, command handler interface methods, and Hadoop metrics APIs.

## Risks
`increaseCommandCount` assumes the command type exists in the initial map; new handlers added later are not tracked. Reusing a single source name can conflict if multiple dispatchers exist in one JVM.

## Test Signals
Signals include metrics records for each handler, received-count increments, optional pool gauges when non-negative, and unregister behavior.
