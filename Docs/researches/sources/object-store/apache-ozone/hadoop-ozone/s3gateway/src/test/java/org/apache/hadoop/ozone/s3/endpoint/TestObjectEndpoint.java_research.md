<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectEndpoint.java

## Purpose
Tests static helper parsing for the S3 copy-source header.

## Important APIs, types, and functions
Exercises `ObjectEndpoint.parseSourceHeader(String)` and its returned Apache Commons `Pair<String,String>`.

## Control flow
One test parses `bucket1/key1`, and another parses `/bucket1/key1`. Both assert the bucket name is `bucket1` and key is `key1`.

## State and persistence behavior
No state is persisted. The helper normalizes request-header syntax before copy operations interact with Ozone buckets.

## Dependencies and integration points
CopyObject and UploadPartCopy depend on this parsing to identify source bucket/key from `x-amz-copy-source`.

## Risks and edge cases
The file does not cover URL-encoded keys, keys containing slashes, empty bucket/key segments, or malformed headers. Those are risk areas for copy-source compatibility.

## Test signals
Passing means both leading-slash and no-leading-slash header forms resolve to the same bucket/key pair.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectEndpoint.java -->
