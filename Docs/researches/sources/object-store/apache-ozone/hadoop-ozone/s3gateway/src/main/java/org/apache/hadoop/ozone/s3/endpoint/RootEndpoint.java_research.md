<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/RootEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/RootEndpoint.java

## Purpose
Top-level S3 gateway endpoint for `GET /`. It lists normal S3 buckets or, when signed for the `s3express` service, lists FSO directory buckets in an S3 Express-compatible response.

## Important APIs, types, and functions
- `get` dispatches between `listAllBuckets` and `listDirectoryBuckets`.
- `isS3ExpressSignedRequest` inspects SigV4 credential scope service segment.
- `listDirectoryBuckets` supports continuation tokens, `max-directory-buckets`, region resolution, ARN construction, and FSO filtering.
- `buildDirectoryBucketArn` formats `arn:aws:s3express:<region>:<account>:bucket/<bucket>`.

## Control flow
Normal listing calls `listS3Buckets` and fills `ListBucketResponse` with owner and bucket metadata. Directory bucket listing decodes optional `continuation-token`, iterates S3 buckets starting after the previous bucket, skips non-FSO layouts, caps the result count, and emits a new continuation token when more buckets remain.

## State and persistence behavior
The endpoint is read-only. It observes bucket metadata and layout state through Ozone client listing. Continuation state is client-visible and encoded by `ContinueToken`.

## Dependencies and integration points
Depends on `EndpointBase.listS3Buckets`, `ListBucketResponse`, `ListDirectoryBucketsResponse`, `DirectoryBucketMetadata`, `ContinueToken`, `S3Owner`, `S3Consts`, audit logging, and list-bucket metrics.

## Risks and edge cases
Continuation only tracks the last emitted bucket name; because non-FSO buckets are skipped after iteration, pagination must not skip later FSO buckets. `max-directory-buckets` is capped at 1000 and rejects negative values. Region comes from credential scope, falling back to `us-east-1`, so malformed or unsigned S3 Express-like requests get default region metadata.

## Test signals
Tests should assert normal bucket XML owner/listing, S3 Express detection from credential scope, max cap and negative-argument failure, continuation token round trip, FSO-only filtering, ARN formatting, and list success/failure metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/RootEndpoint.java -->
