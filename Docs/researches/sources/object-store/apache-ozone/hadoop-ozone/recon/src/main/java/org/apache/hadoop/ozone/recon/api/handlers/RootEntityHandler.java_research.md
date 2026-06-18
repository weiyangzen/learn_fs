<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/RootEntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/RootEntityHandler.java

## Purpose

`RootEntityHandler` implements namespace APIs for the root path `/` across all volumes and buckets.

## Important APIs and Types

It returns root `NamespaceSummaryResponse`, aggregate `DUResponse`, cluster-wide quota, and file-size distribution. It reads `OmVolumeArgs`, `OmBucketInfo`, optional root `OmPrefixInfo`, `SCMNodeStat`, and `NSSummary` rows.

## Control Flow

Summary lists all volumes and buckets, recursively counts directories and keys under every bucket, and includes root prefix metadata if present. DU iterates volumes and their buckets, sums materialized sizes, optionally calculates replicated bucket DU through layout-specific bucket handlers, emits per-volume rows, and sorts if requested. Quota uses SCM total capacity and root replicated DU. Distribution folds all bucket distributions.

## State and Persistence

No writes occur. Data comes from OM metadata tables, namespace summaries, and live SCM node stats.

## Dependencies and Integration Points

It is selected by `EntityHandler` for `/` and uses `BucketHandler` factories for replica-aware DU across layouts.

## Risks and Edge Cases

Replica-aware root DU can be expensive because it visits every bucket. Missing namespace summaries lower aggregate counts/sizes. Quota used is replicated bytes, unlike some lower-level quota handlers. Root prefix metadata may be absent and returns an empty object.

## Test Signals

Tests should cover empty clusters, multiple volumes/buckets, replica and non-replica DU, sorting limits, prefix metadata presence/absence, quota capacity, and distribution aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/RootEntityHandler.java -->
