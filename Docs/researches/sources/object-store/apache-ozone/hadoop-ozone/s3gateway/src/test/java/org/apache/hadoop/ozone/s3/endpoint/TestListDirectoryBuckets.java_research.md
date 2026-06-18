<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListDirectoryBuckets.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListDirectoryBuckets.java

## Purpose
Tests S3 Express-style directory bucket listing from `RootEndpoint`, backed by Ozone FSO buckets.

## Important APIs, types, and functions
Uses `RootEndpoint.get`, `ListDirectoryBucketsResponse`, `DirectoryBucketMetadata`, `BucketArgs` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `SignatureInfo` credential scopes, and query params `MAX_DIRECTORY_BUCKETS` and `CONTINUATION_TOKEN`.

## Control flow
Setup creates an `OzoneClientStub`, a root endpoint with a V4 `s3express` credential scope, and the default S3 volume. Tests cover empty output, filtering object-store buckets out of directory-bucket output, pagination over five FSO buckets, zero/invalid max values, credential-scope region selection, and max capping above the supported limit.

## State and persistence behavior
The stub object store holds created volumes and buckets. Only FSO buckets should appear in the directory bucket response. Continuation tokens encode list position; response metadata includes name, creation time, region, and generated bucket ARN.

## Dependencies and integration points
This bridges S3 root listing, S3 Express signing metadata, Ozone bucket layout, and ARN construction through `RootEndpoint.buildDirectoryBucketArn`.

## Risks and edge cases
The tests assume deterministic bucket listing order from the stub. They do not cover malformed continuation tokens, mixed owner IDs, or live OM pagination behavior.

## Test signals
Assertions check bucket counts, names, region extraction (`us-west-2` or `aws-global`), continuation token presence, and invalid max-bucket exception behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListDirectoryBuckets.java -->
