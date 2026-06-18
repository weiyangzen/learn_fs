# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcDetailedMetrics.java

## Purpose
`RpcDetailedMetrics` publishes per-RPC-method timing rates through Hadoop metrics. It complements aggregate `RpcMetrics` by tracking method-name-specific processing samples.

## Important APIs, types, and functions
- Metrics source annotation: `@Metrics(about="Per method RPC metrics", context="rpcdetailed")`.
- `create(int port)` constructs and registers a metrics source named `RpcDetailedActivityForPort<port>`.
- `init(Class<?> protocol)` initializes `MutableRatesWithAggregation` from protocol methods.
- `addProcessingTime(String rpcCallName, long processingTime)` records a sample for a named RPC call.
- `shutdown()` unregisters the metrics source.

## Control flow
The constructor tags the registry with the RPC port. Registration goes through `DefaultMetricsSystem.instance().register`. Calls from `Server.updateMetrics` add samples after subtracting lock wait time from processing time.

## State and persistence behavior
State is in-memory metrics registry and mutable rate aggregation. No durable persistence exists; metrics are exposed through the process metrics system until `shutdown`.

## Dependencies and integration points
It depends on Hadoop metrics2 annotations and mutable metrics types. It is created by `Server` and consumed by JMX/metrics sinks configured for the Hadoop process.

## Risks and edge cases
Metric source names are port-based, so duplicate servers on the same port in one process would conflict. Dynamic method names can expand metric cardinality if call names are not controlled. `rates` is injected by metrics2 annotation processing; direct construction outside metrics registration may leave it unset.

## Test signals
Tests should verify registration name/tag, method initialization from a protocol class, adding processing samples, duplicate registration behavior, and source unregistration on shutdown.
