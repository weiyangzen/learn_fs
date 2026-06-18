# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerTransportFilter.java

## Purpose

`GrpcMetricsServerTransportFilter` tracks active gRPC client connections. The complete 47-line source was read for this report.

## Important APIs, Types, and Functions

It extends `ServerTransportFilter` and overrides `transportReady` and `transportTerminated`.

## Control Flow

When a transport becomes ready, it increments active client connections and delegates to the superclass. When a transport terminates, it decrements the counter and delegates.

## State and Persistence Behavior

It holds a `GrpcMetrics` reference. Metrics are in-memory and exported by Hadoop metrics sinks.

## Dependencies and Integration Points

It depends on gRPC `Attributes` and `ServerTransportFilter`, and is installed on Ozone gRPC servers alongside interceptors.

## Risks and Edge Cases

Counter correctness depends on one termination event per ready event. The `GrpcMetrics` field is mutable and not final. Negative counts are possible if termination is observed without a matching ready or if duplicate termination occurs.

## Test Signals

Tests should cover ready/terminated increments, duplicate events, and integration with server lifecycle.
