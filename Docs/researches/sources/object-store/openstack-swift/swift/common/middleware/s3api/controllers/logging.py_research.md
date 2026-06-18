# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/logging.py

Purpose: Provides partial bucket logging subresource compatibility.

Important APIs and control flow: `LoggingStatusController.GET` is public, bucket-scoped, verifies bucket existence with a Swift HEAD, and always returns an empty `BucketLoggingStatus` XML document, representing logging disabled. `PUT` is public and bucket-scoped but raises `S3NotImplemented`. Both methods use `bucket_operation(err_resp=NoLoggingStatusForKey)` so key-qualified logging requests produce the S3-specific error instead of silently coercing.

State, dependencies, and integration: No persistent logging state is read or written. It depends on the common controller decorator and XML serialization.

Risks and test signals: The controller advertises read compatibility but not configuration support. Tests should cover GET for bucket and key paths, PUT 501 behavior, missing bucket error propagation, and XML body shape for disabled logging.
