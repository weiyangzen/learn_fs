# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/__init__.py

Purpose: Collects and re-exports S3 API controller classes from the controllers package.

Important APIs and control flow: Imports the base `Controller` and `UnsupportedController`, account service, bucket, object, ACL, S3 ACL, multi-delete, multipart upload, location, logging, versioning, tagging, and object-lock controllers. `__all__` defines the public names used by request routing and imports elsewhere in s3api.

State, dependencies, and integration: No runtime state beyond module imports. It is an integration point for `s3request` controller resolution and keeps controller names centralized.

Risks and test signals: Adding a controller without updating this file can break request dispatch or package exports. Tests should import every `__all__` symbol and verify request routing still maps subresources to the expected controller classes.
