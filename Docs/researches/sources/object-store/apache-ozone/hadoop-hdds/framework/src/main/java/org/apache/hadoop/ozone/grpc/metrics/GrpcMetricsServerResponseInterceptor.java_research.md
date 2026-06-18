# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerResponseInterceptor.java

## Purpose

`GrpcMetricsServerResponseInterceptor` records serialized byte counts for gRPC responses and unknown response message counts. The complete 64-line source was read for this report.

## Important APIs, Types, and Functions

The class implements `ServerInterceptor` and overrides `interceptCall`, wrapping the `ServerCall` with `ForwardingServerCall.SimpleForwardingServerCall` and overriding `sendMessage`.

## Control Flow

For each outbound response, `sendMessage` calculates serialized size if the message is a protobuf `AbstractMessage`, otherwise increments unknown sent message count. It increments sent bytes and then delegates to the real server call.

## State and Persistence Behavior

No local persistent state is stored. Metrics are accumulated in `GrpcMetrics`.

## Dependencies and Integration Points

It depends on gRPC server call/interceptor APIs, protobuf `AbstractMessage`, and `GrpcMetrics`.

## Risks and Edge Cases

Non-protobuf messages count as unknown and contribute zero bytes. The raw `ForwardingServerCall` instantiation omits generic diamond syntax but functions. Exceptions from `getSerializedSize` or downstream send are not handled locally.

## Test Signals

Tests should cover protobuf response byte counts, unknown response counters, multiple response messages, and delegation ordering.
