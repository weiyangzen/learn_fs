<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketUtilizationMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketUtilizationMetrics.java

Purpose: Unit test for bucket utilization metrics emission from OM bucket metadata.

Important APIs/types/functions: Mocks `OMMetadataManager.getBucketIterator`, `MetricsCollector`, and `MetricsRecordBuilder`. Uses `BucketUtilizationMetrics` and `BucketMetricsInfo` metric/tag descriptors. `createMockEntry` builds cache entries containing mocked `OmBucketInfo`.

Control flow: The test creates two bucket cache entries, one with a finite byte quota and one with `QUOTA_RESET`. It configures iterator and metrics builder mocks, calls `getMetrics`, and verifies tags and gauges emitted for volume, bucket, used bytes, snapshot used bytes, quota bytes, quota namespace, and available bytes.

State and persistence behavior: No persistence. It simulates cache-backed bucket metadata and observes metric builder calls. Available bytes are expected to be quota minus used minus snapshot for finite quota, and `QUOTA_RESET` for reset quota.

Dependencies and integration points: Protects integration between OM metadata iteration and Hadoop Metrics2 export for per-bucket utilization.

Risks: Mock-based verification checks calls but not final metrics records as a metrics system would expose them. It covers two buckets and quota reset but not deleted/null cache values or negative availability.

Test signals: Passing means metric collection iterates buckets and emits expected tags/gauges for normal and unlimited quotas.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketUtilizationMetrics.java -->
