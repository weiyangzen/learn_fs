<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketEntityHandler.java

## Purpose

`BucketEntityHandler` implements namespace summary, disk usage, quota, and file-size distribution behavior for bucket-level paths.

## Important APIs and Types

It extends `EntityHandler` and uses a layout-specific `BucketHandler`. It returns `BucketObjectDBInfo`, `CountStats`, `DUResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse`.

## Control Flow

Summary resolves the bucket object id, counts recursive directories and keys from `NSSummary`, and returns bucket metadata from the OM bucket table. DU loads the bucket NSSummary, adds child-directory disk usage rows, optionally adds direct keys through `BucketHandler.handleDirectKeys`, sorts if requested, and returns aggregate size values. Quota reads the bucket's quota and total namespace size. Distribution recursively accumulates file-size buckets.

## State and Persistence

No state is written. Reads come from OM bucket table and Recon namespace summary table.

## Dependencies and Integration Points

It is created by `EntityType.BUCKET` through `EntityHandler` and delegates layout-sensitive direct-key behavior to `FSOBucketHandler`, `LegacyBucketHandler`, or `OBSBucketHandler`.

## Risks and Edge Cases

An empty bucket with no NSSummary returns a mostly empty DU response. Child NSSummary lookups are not null-checked before dereferencing. Quota calculation uses unreplicated total size, while root quota uses replicated size. Sorting is limited by `DISK_USAGE_TOP_RECORDS_LIMIT`.

## Test Signals

Tests should cover empty buckets, child directories, direct file listing, replica DU, sorting, quota values, missing bucket metadata, and all bucket layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/BucketEntityHandler.java -->
