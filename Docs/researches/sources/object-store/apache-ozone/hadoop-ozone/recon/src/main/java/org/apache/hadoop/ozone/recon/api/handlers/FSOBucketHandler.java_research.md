<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/FSOBucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/FSOBucketHandler.java

## Purpose

`FSOBucketHandler` implements bucket strategy logic for file-system-optimized buckets, where directories and files are keyed by volume id, bucket id, parent object id, and name.

## Important APIs and Types

It implements path classification, directory object-id lookup, file lookup, directory lookup, direct-key DU, and replicated DU calculation. It uses OM directory and file tables and `NSSummary` materialized totals.

## Control Flow

Construction resolves and stores volume and bucket object IDs. `determineKeyPath` walks path components from the bucket id, checking the directory table at each component and the file table for the leaf when no directory exists. `handleDirectKeys` seeks the file table by object-id prefix and emits direct child files. `getDirObjectId` walks directory table rows up to a cutoff.

## State and Persistence

The handler stores volumeId and bucketId only. It reads OM metadata and namespace summary tables; no writes occur.

## Dependencies and Integration Points

It is selected for `BucketLayout.FILE_SYSTEM_OPTIMIZED` by `BucketHandler` and supports namespace entity handlers plus key insight FSO path conversion.

## Risks and Edge Cases

Missing intermediate directories return UNKNOWN; missing leaf directory and file also returns UNKNOWN. `getDirObjectId` silently returns the last found object id if an intermediate component is missing, so callers depend on prior classification. Direct-key enumeration assumes RocksDB prefix ordering. `getDirInfo` requires at least volume/bucket/dir.

## Test Signals

Tests should cover nested directories, leaf files, missing intermediates, empty directories, direct-file DU with and without replica/listing, directory object-id cutoff, and object-id prefix seek boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/FSOBucketHandler.java -->
