# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/base.py

Purpose: Defines shared decorators and base classes for S3 API controllers.

Important APIs and control flow: `bucket_operation` ensures a handler acts on a bucket, either clearing `req.object_name` when a key was provided or raising a configured S3 error. `object_operation` requires an object key and raises `InvalidRequest` otherwise. `check_container_existence` forces `req.get_container_info(self.app)` before running the decorated handler. `Controller` stores `app`, `conf`, and `logger`, and exposes `resource_type` by converting the class name without `Controller` to upper snake case. `UnsupportedController` raises `S3NotImplemented` during construction.

State, dependencies, and integration: State is controller instance references only. The decorators mutate request attributes or trigger container-info side effects used by downstream Swift request construction.

Risks and test signals: Decorator order matters for access checks and error semantics. Tests should cover bucket handlers with accidental object keys, object handlers without keys, custom `err_resp`, container existence failures, and resource type strings used in `MethodNotAllowed`.
