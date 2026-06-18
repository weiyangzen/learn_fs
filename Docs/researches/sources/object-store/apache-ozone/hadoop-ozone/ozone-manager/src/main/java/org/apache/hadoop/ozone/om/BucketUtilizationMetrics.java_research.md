# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketUtilizationMetrics.java

## Purpose

`BucketUtilizationMetrics` is a Hadoop metrics source that emits per-bucket capacity and quota metrics from OM metadata.

## Important APIs and Types

- `create(OMMetadataManager)` registers a metrics source with `DefaultMetricsSystem`.
- `getMetrics(MetricsCollector, boolean)` iterates bucket metadata and emits gauges/tags.
- `unRegister()` unregisters the source.
- `BucketMetricsInfo` defines tag/gauge names and descriptions.

## Control Flow

On collection, the source obtains `metadataManager.getBucketIterator()`, skips null cache values, computes available space as `-1` when quota is unset or `max(quota - totalBucketSpace, 0)` otherwise, and adds one metrics record per bucket with volume and bucket tags plus used bytes, snapshot used bytes, quota bytes, quota namespace, and available bytes.

## State and Persistence

The class holds only an `OMMetadataManager` reference. Metrics are live observations from OM metadata/cache, not persisted by this class.

## Dependencies and Integration Points

It integrates with Hadoop metrics2, `DefaultMetricsSystem`, OM metadata bucket iterators, `OmBucketInfo`, and `OzoneConsts.OZONE` metrics context.

## Risks and Edge Cases

Metric cardinality grows with bucket count because one record is emitted per bucket. Iteration over cache/table state must tolerate deleted buckets as null cache values. The source name is class-simple-name based, so double registration without unregister can conflict.

## Test Signals

Tests should verify registration/unregistration, metrics for quota/unlimited quota, snapshot usage, null cache skips, and large-bucket-count behavior.
