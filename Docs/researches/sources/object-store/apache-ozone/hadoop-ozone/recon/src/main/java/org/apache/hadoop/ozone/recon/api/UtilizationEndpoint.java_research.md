<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/UtilizationEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/UtilizationEndpoint.java

## Purpose

`UtilizationEndpoint` exposes file-size and container-size distribution counts from Recon persistence under `/utilization`.

## Important APIs and Types

`/fileCount` returns `FileCountBySize` rows filtered by volume, bucket, and optional file size upper bound. `/containerCount` returns `ContainerCountBySize` rows filtered by a normalized container-size upper bound. It uses `ReconFileMetadataManager`, `ContainerCountBySizeDao`, `UtilizationSchemaDefinition`, and jOOQ.

## Control Flow

For exact volume+bucket+fileSize requests, it directly looks up a `FileSizeCountKey`. Otherwise it iterates the RocksDB file-count table and filters records in Java. Container counts normalize the upper bound with `ReconUtils.getContainerSizeUpperBound`; positive inputs query by id, while non-positive inputs return all positive-count records.

## State and Persistence

The endpoint is read-only. File counts come from a RocksDB table managed by `ReconFileMetadataManager`; container counts come from the SQL/jOOQ utilization schema.

## Dependencies and Integration Points

It depends on Recon file metadata tasks that populate file count buckets and container utilization tasks that populate the jOOQ table.

## Risks and Edge Cases

Partial file filters require a full table scan. `fileSize <= 0` with volume and bucket scans all sizes rather than rejecting. Container-size normalization means the returned row may not match the raw requested bound. Errors are logged and returned as generic HTTP 500 without body.

## Test Signals

Tests should cover exact and filtered file-count lookup, empty/zero counts, iterator closure, volume-only and bucket-only filters, container upper-bound normalization, all-positive container rows, and persistence exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/UtilizationEndpoint.java -->
