# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListDirectoryBucketsResponse.java

Purpose: `ListDirectoryBucketsResponse` is the JAXB model for S3 directory bucket listing responses.

Important APIs and flow: it wraps a `Buckets` list of `DirectoryBucketMetadata` and exposes an optional `ContinuationToken`. The root endpoint populates bucket rows and continuation state.

State, dependencies, risks, and tests: state is response-only. It integrates with directory-bucket list APIs and directory bucket metadata. Risks include incomplete AWS compatibility around continuation, region, and ARN fields. Tests should assert XML wrapping and continuation token behavior.
