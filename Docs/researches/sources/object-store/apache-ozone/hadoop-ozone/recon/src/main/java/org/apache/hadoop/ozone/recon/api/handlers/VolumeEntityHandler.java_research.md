<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/VolumeEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/VolumeEntityHandler.java

## Purpose

`VolumeEntityHandler` implements namespace APIs for volume-level paths.

## Important APIs and Types

It returns `VolumeObjectDBInfo`, aggregate `CountStats`, `DUResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse` for all buckets under a volume.

## Control Flow

Summary lists buckets under the volume and accumulates recursive directory/key counts. DU builds one row per bucket, sums materialized sizes, optionally calculates replicated DU through each bucket's `BucketHandler`, and sorts rows. Quota reads volume quota and sums unreplicated bucket sizes. Distribution aggregates file-size buckets from all child buckets.

## State and Persistence

The handler writes nothing. It reads OM volume/bucket tables and namespace summary rows.

## Dependencies and Integration Points

It is selected by `EntityHandler` after confirming volume existence. It uses `BucketHandler` only when replica-aware DU is requested.

## Risks and Edge Cases

Replica-aware DU can be expensive for many buckets. Missing bucket summaries reduce totals. Volume quota usage is unreplicated while root quota usage is replicated, so clients must understand the unit difference.

## Test Signals

Tests should cover empty volume, multiple buckets, replica DU, sorting, quota, missing volume metadata, distribution aggregation, and bucket layout mix.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/VolumeEntityHandler.java -->
