<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/metrics/TestS3GatewayMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/metrics/TestS3GatewayMetrics.java

## Purpose
Broad unit suite verifying `S3GatewayMetrics` success/failure counters and latency metric registration across bucket, object, multipart, copy, ACL, and tagging endpoints.

## Important APIs, types, and functions
Uses `S3GatewayMetrics` getters, `MetricsCollectorImpl`, `BucketEndpoint`, `RootEndpoint`, `ObjectEndpoint`, `EndpointTestUtils`, `OzoneClientStub`, `S3ErrorTable`, ACL fixture XML, and query params for ACL/list parts/multipart operations.

## Control flow
Setup creates a bucket/key fixture and endpoints sharing the same metrics instance. Each test snapshots a metric counter, performs a success or intentional failure, and asserts a delta of one. Covered paths include bucket head/list/get/create/delete, bucket ACL get/put, object head/get/put/delete, multipart initiate/abort/complete/upload-part/list-parts, copy object, and object tagging get/put/delete. The final test exports metrics and checks PutObjectAcl latency metric names are present.

## State and persistence behavior
Stub object-store state is mutated to trigger endpoint behavior. Metrics state is in-process counters and latency snapshots; each endpoint call should increment exactly the matching success or failure counter.

## Dependencies and integration points
This ties endpoint exception handling to metrics accounting and Hadoop metrics2 export.

## Risks and edge cases
Exact delta assertions can break when a single user request starts incrementing additional counters. The tests validate counters, not latency values.

## Test signals
Signals are one-count deltas for each metric getter, expected S3 errors on failures, successful response statuses, and exported latency metric names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/metrics/TestS3GatewayMetrics.java -->
