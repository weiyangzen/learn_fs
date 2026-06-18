<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestRootList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestRootList.java

## Purpose
Tests root-level S3 bucket listing.

## Important APIs, types, and functions
Uses `RootEndpoint.get`, `ListBucketResponse`, `OzoneClientStub`, default S3 volume config, and `S3Owner.DEFAULT_S3OWNER_ID`.

## Control flow
Setup creates the default S3 volume and root endpoint. The test first lists with no buckets and expects zero. It then creates ten S3 buckets and verifies the response count and owner display/id fields.

## State and persistence behavior
The stub object store persists volume and bucket names. Root listing should reflect current buckets without mutating state.

## Dependencies and integration points
This covers the root endpoint's object-store list integration and response owner metadata.

## Risks and edge cases
Pagination, directory bucket filtering, permissions, and ordering are not covered here; directory bucket listing is covered separately.

## Test signals
Signals are bucket counts of zero and ten plus owner display name `root` and default owner ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestRootList.java -->
