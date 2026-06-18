# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/object_lock.py

Purpose: Provides explicit object-lock subresource responses for unsupported S3 Object Lock configuration.

Important APIs and control flow: `ObjectLockController.GET` is public and bucket-scoped, but always raises `ObjectLockConfigurationNotFoundError` for the bucket. `PUT` is public and bucket-scoped, and raises `S3NotImplemented` with the generic unimplemented resource message.

State, dependencies, and integration: No persistent state is read or written. It depends on base controller decorators and s3response exception classes.

Risks and test signals: The controller must return the S3-compatible "not configured" error for GET while returning 501 for configuration attempts. Tests should cover bucket-only coercion, missing bucket propagation if ACL/existence checks happen before dispatch, GET error code/body, and PUT unimplemented behavior.
