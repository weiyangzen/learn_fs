# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcMetrics.java

## Purpose
`RpcMetrics` publishes aggregate IPC server metrics: bytes sent/received, queue time, lock wait time, processing time, authentication/authorization counters, client backoff count, slow-RPC count, open connections, per-user connections, queue length, and dropped connections.

## Important APIs, types, and functions
- Metrics source annotation: `@Metrics(about="Aggregate RPC metrics", context="rpc")`.
- `create(Server, Configuration)` registers `RpcActivityForPort<port>`.
- Public metrics methods expose server-derived gauges: `numOpenConnections`, `numOpenConnectionsPerUser`, `callQueueLength`, and `numDroppedConnections`.
- Increment methods record auth, authorization, sent/received byte, client backoff, and slow-call events.
- `addRpcQueueTime`, `addRpcLockWaitTime`, and `addRpcProcessingTime` record rates and optional quantiles.
- Inspection helpers expose processing sample count, mean, stddev, slow calls, and registry tags.

## Control flow
Construction tags metrics with port and server name, reads percentile intervals and quantile enablement from configuration, and creates quantile metrics per interval when enabled. The server calls increment/add methods from read/write paths, auth paths, queue overflow paths, and handler completion.

## State and persistence behavior
All state lives in metrics2 mutable counters/rates/quantiles. It is not durable and is removed from the default metrics system on `shutdown`.

## Dependencies and integration points
It depends on `Server` for live gauge values, Hadoop `CommonConfigurationKeys` for quantile settings, and metrics2 classes. It is tightly integrated into `Server` request lifecycle and is visible to metrics sinks/JMX.

## Risks and edge cases
Port-based source names can collide in multi-server tests. Quantile arrays remain null when disabled; add methods guard with `rpcQuantileEnable`. Rate statistics used for slow-RPC detection depend on metrics snapshot behavior, so early sample counts and reset windows affect classification.

## Test signals
Tests should validate counters, rates, quantile creation by intervals, disabled quantile paths, server gauge delegation, slow-RPC counter behavior, processing mean/stddev accessors, tag retrieval, and unregister behavior.
