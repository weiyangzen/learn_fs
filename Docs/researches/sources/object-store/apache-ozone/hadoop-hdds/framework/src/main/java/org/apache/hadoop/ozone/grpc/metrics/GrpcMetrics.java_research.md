# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetrics.java

## Purpose

`GrpcMetrics` is a Hadoop metrics2 source for Ozone gRPC byte counters, message classification counters, queue/processing latency rates and quantiles, active client connections, and latest request type. The complete 224-line source was read for this report.

## Important APIs, Types, and Functions

Important APIs include static `create`, `unRegister`, `getMetrics`, byte/message increment methods, `addGrpcQueueTime`, `addGrpcProcessingTime`, connection count increment/decrement, getters for counters/rates, and request type setter/getter.

## Control Flow

Construction creates a `MetricsRegistry`, reads percentile interval configuration, and creates queue/processing `MutableQuantiles` arrays if enabled. `create` registers the source in the default metrics system. `getMetrics` snapshots the registry and adds a second record tagged with latest request type. Latency methods update the mutable rate and optional quantiles.

## State and Persistence Behavior

State is in-memory metrics counters/rates/quantiles. Persistence/export is handled by Hadoop metrics sinks. `unRegister` unregisters the source and stops quantile helpers.

## Dependencies and Integration Points

It depends on Hadoop metrics2, Ozone config keys/constants, `MetricUtil`, and is updated by the gRPC server interceptors and transport filter in this package.

## Risks and Edge Cases

Queue/processing time methods accept `int` values, while interceptors pass nanosecond differences cast to int even though metric names say milliseconds. `requestType` is a single mutable string shared across concurrent calls. Registration uses a fixed source name, so multiple instances may conflict.

## Test Signals

Tests should verify metrics registration/unregistration, byte counters, unknown message counters, quantile creation by config, active connection counts, request type tagging, and latency unit expectations.
