<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/S3GatewayMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/S3GatewayMetrics.java

## Purpose
Metrics2 source for S3 gateway operation counters, byte counters, list counts, and latency distributions.

## Important APIs, types, and functions
- Singleton lifecycle is managed by `create`, `unRegister`, `getMetrics`, and `close`.
- Counter groups cover bucket endpoints, root listing, object operations, multipart operations, object tagging, object ACL, and byte totals.
- Latency metrics are `PerformanceMetrics` instances initialized from configured percentile intervals.
- `getMetrics(MetricsCollector, boolean)` snapshots every counter and latency metric.
- `update*SuccessStats`, `update*FailureStats`, and `inc*Length` methods mutate counters and latency distributions.

## Control flow
Gateway startup calls `create` to register the source with the default metrics system. Endpoints call update methods at success/failure boundaries using request `startNanos`. Some update methods return elapsed nanoseconds so endpoint audit performance strings can include the same latency.

## State and persistence behavior
Metrics are in-memory process state registered with Hadoop Metrics2. They are not persisted here, but exported to configured metrics sinks/JMX. `close` shuts down percentile resources.

## Dependencies and integration points
Used by `Gateway`, `BucketEndpoint`, `RootEndpoint`, `ObjectEndpoint`, `ObjectEndpointStreaming`, tagging/ACL handlers, and tests. Depends on `DefaultMetricsSystem`, `MutableCounterLong`, `MetricsRegistry`, `PerformanceMetrics`, and S3 gateway config percentile intervals.

## Risks and edge cases
The singleton can be null if endpoints call `getMetrics` before gateway startup. `unRegister` closes the instance and unregisters the source; repeated tests must clean up to avoid stale counters. New endpoint operations require adding fields, snapshot entries, update methods, getters, and tests together.

## Test signals
`TestS3GatewayMetrics` exercises operation success/failure deltas for bucket, object, MPU, tagging, and byte counters. Metrics-source tests should also verify singleton lifecycle, snapshot names, latency increments, and cleanup between tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/S3GatewayMetrics.java -->
