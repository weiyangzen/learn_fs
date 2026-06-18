# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/service.py

Purpose: Implements account-level `GET Service`, listing the user's S3 buckets based on Swift account container listings.

Important APIs and control flow: `ServiceController.GET` requests the Swift account listing as JSON, filters container names through `validate_bucket_name` with the configured DNS-compliance mode, builds `ListAllMyBucketsResult`, and emits owner and bucket XML. Bucket creation dates are synthetic and fixed because Swift container listings do not preserve S3 creation timestamps. When `s3_acl` and `check_bucket_owner` are enabled, each candidate bucket is HEADed and hidden if it returns `AccessDenied` or `NoSuchBucket`.

State, dependencies, and integration: No state is changed. It depends on Swift account listing JSON, bucket-name validation, ACL-aware HEAD behavior, and XML helpers.

Risks and test signals: Owner filtering can add many HEAD subrequests and may hide buckets based on transient access results. Tests should cover bucket-name filtering, malformed listing JSON behavior, owner XML, fixed creation date, ACL owner filtering, and AccessDenied/NoSuchBucket skip behavior.
