# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerRequestInterceptor.java

## Purpose

`GrpcMetricsServerRequestInterceptor` records received gRPC request sizes, request type, queue time, and processing time. The complete 98-line source was read for this report.

## Important APIs, Types, and Functions

The class implements `ServerInterceptor` with `interceptCall`. It wraps the listener in `SimpleForwardingServerCallListener` and overrides `onMessage` and `onComplete`.

## Control Flow

`interceptCall` stores `receivedTime` and starts the downstream call. `onMessage` records `startTime`, measures serialized size for protobuf `AbstractMessage`, increments unknown-message counter otherwise, increments received bytes, parses the first line of `message.toString()` as `cmdType`, updates metrics request type, then delegates. `onComplete` delegates, stores `endTime`, computes queue and processing deltas, and records them.

## State and Persistence Behavior

The interceptor stores timing fields as instance variables, not per-call local state. Metrics are in-memory in `GrpcMetrics` and exported by Hadoop metrics sinks.

## Dependencies and Integration Points

It depends on gRPC server interceptor APIs, protobuf `AbstractMessage`, and `GrpcMetrics`. It is installed on Ozone gRPC servers.

## Risks and Edge Cases

Instance fields make concurrent calls race if one interceptor instance handles multiple calls. Parsing request type from `toString()` assumes a non-empty first line with a colon. Nanosecond differences are cast to `int` and recorded as metric values named milliseconds. Unknown non-protobuf messages still call `toString()` and parsing can fail.

## Test Signals

Tests should cover protobuf and non-protobuf requests, malformed `toString`, concurrent calls, queue/processing time units, and request type extraction.
