<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/OBSBucketHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/OBSBucketHandler.java

## Purpose

`OBSBucketHandler` implements object-store bucket behavior, treating bucket contents as flat keys without directory support.

## Important APIs and Types

It uses the object-store key table, `OmKeyInfo`, `NSSummary`, and `DUResponse.DiskUsage`, and returns `BucketLayout.OBJECT_STORE`.

## Control Flow

`determineKeyPath` builds `/vol/bucket/key`, seeks the key table, and returns KEY only on exact match. `handleDirectKeys` seeks all keys under `/vol/bucket/`, emits every key if requested, and computes replicated direct-key totals. Directory lookup methods throw `UnsupportedOperationException`.

## State and Persistence

The handler stores volume, bucket, and bucket info. It reads OM key and namespace summary tables only.

## Dependencies and Integration Points

It is selected for `OBJECT_STORE` buckets and for legacy buckets when filesystem paths are disabled. Entity path parsing preserves slash-containing key names for this layout.

## Risks and Edge Cases

Because object-store keys may contain slashes, clients can see subpaths that are object names rather than directories. Directory APIs are invalid by design. Direct-key listing ignores `normalizedPath` when setting subpath and returns the raw object name.

## Test Signals

Tests should cover exact flat key lookup, slash-containing object names, unknown pseudo-directory paths, direct-key listing, replica DU, and unsupported directory calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/OBSBucketHandler.java -->
