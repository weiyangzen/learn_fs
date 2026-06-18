# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/location.py

Purpose: Implements `GET ?location` for buckets.

Important APIs and control flow: `LocationController.GET` is public and bucket-scoped. It HEADs the bucket through Swift to verify existence and authorization, builds a `LocationConstraint` XML document, leaves it empty for the S3 default `us-east-1`, otherwise writes the configured `self.conf.location`, and returns `HTTPOk` with `application/xml`.

State, dependencies, and integration: No persistent state is changed. It depends on the bucket operation decorator, `req.get_response`, and the s3api XML helpers.

Risks and test signals: The empty-body semantics for `us-east-1` are compatibility-sensitive. Tests should cover existing bucket verification, object-key requests being coerced to bucket requests, default versus non-default region output, and correct XML namespace/declaration behavior.
