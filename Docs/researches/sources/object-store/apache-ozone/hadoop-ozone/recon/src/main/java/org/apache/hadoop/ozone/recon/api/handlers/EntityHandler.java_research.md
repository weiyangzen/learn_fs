<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/EntityHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/EntityHandler.java

## Purpose

`EntityHandler` is the abstract dispatcher and shared aggregation base for Recon namespace summary paths.

## Important APIs and Types

It defines abstract methods for summary, DU, quota, and distribution responses. Static `getEntityHandler` classifies paths as root, volume, bucket, directory, key, or unknown. Helpers include recursive `getTotalFileSizeDist`, `getTotalDirCount`, `getTotalKeyCount`, `getTotalSize`, `parseRequestPath`, `parseObjectStorePath`, and `normalizePath`.

## Control Flow

Classification normalizes the input path, parses names, checks root and volume existence, resolves the bucket handler, and delegates key-path classification to bucket layout strategies. For object-store buckets it preserves slash-containing key names via `parseObjectStorePath`; other layouts split each path component.

## State and Persistence

Instances store managers, bucket handler, normalized path, and parsed names. They read OM metadata and namespace summary tables but do not write.

## Dependencies and Integration Points

It is the central integration point between `NSSummaryEndpoint`, `EntityType` factory methods, `BucketHandler`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, and SCM.

## Risks and Edge Cases

`parseRequestPath` returns `['']` for some empty strings, so callers rely on earlier validation. `parseObjectStorePath` effectively returns up to three parts and its null branch is unreachable for Java `split` with limit 3. Recursive distribution still walks children even though key count and size are materialized. Unknown handling constructs an `UnknownEntityHandler` with null path, which relies on default layout normalization not being dereferenced in response methods.

## Test Signals

Tests should cover path normalization, root handling, missing volume/bucket, object-store slash keys, legacy filesystem path mode, FSO directory/key classification, recursion helpers, and unknown path responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/handlers/EntityHandler.java -->
