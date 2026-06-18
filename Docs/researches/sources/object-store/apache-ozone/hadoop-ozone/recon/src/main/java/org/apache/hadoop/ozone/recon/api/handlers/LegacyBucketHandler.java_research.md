<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/LegacyBucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/LegacyBucketHandler.java

## Purpose

`LegacyBucketHandler` implements filesystem-style namespace behavior for legacy buckets when filesystem paths are enabled.

## Important APIs and Types

It uses the legacy key table, directory-marker keys, `OmKeyInfo`, `NSSummary`, and `DUResponse.DiskUsage`. It returns `BucketLayout.LEGACY`.

## Control Flow

`determineKeyPath` removes trailing slash, builds `/vol/bucket/key`, seeks the key table, and classifies exact match as KEY or exact match with trailing slash as DIRECTORY. `handleDirectKeys` seeks under a bucket or directory prefix, skips deeper descendants and directory markers, and optionally emits direct key rows. `getDirObjectId` builds the directory marker key ending in slash and returns its object id.

## State and Persistence

The handler stores volume, bucket, and bucket info. It reads key table and namespace summaries, with no writes.

## Dependencies and Integration Points

It is selected only for legacy buckets when OM filesystem paths are enabled. Entity handlers rely on it to make legacy marker directories look like directories.

## Risks and Edge Cases

Directory detection requires a marker key with a trailing slash. `getDirInfo` constructs only a minimal `OmDirectoryInfo` with `names[2]`, so deeper directory metadata can be imprecise. Direct-key depth filtering is string-split based and can be sensitive to path normalization. Missing directory marker throws `IOException`.

## Test Signals

Tests should cover exact key, marker directory, unknown path, nested direct-key filtering, marker skipping, directory object-id lookup, and legacy mode selection via config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/LegacyBucketHandler.java -->
