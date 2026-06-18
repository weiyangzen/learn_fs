# sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_handlers.py

Purpose: Provides per-controller ACL enforcement logic for S3 API requests, keeping permission checks out of controller business logic.

Important APIs and control flow: `get_acl_handler` maps controller names to handler classes. `BaseAclHandler` creates scoped handler copies, dispatches method-specific ACL logic, HEADs object or container resources to retrieve ACLs, maps S3 method plus Swift method/resource through `ACL_MAP`, and checks the current user against the required permission. `get_acl` parses canned grant headers or XML bodies into `ACL` objects. Specialized handlers implement bucket creation ACL writes, object PUT ACL capture, S3 ACL subresource read/write, multi-object delete bucket-write checks, and multipart upload behavior where base bucket ACLs are checked once and temporary object ACL metadata is copied from upload markers to final manifests.

State, dependencies, and integration: State is per-request handler context, request headers, and flags like multipart `acl_checked`. It depends on `subresource.ACL`, sysmeta header helpers, XML validation, and `req.get_acl_response`.

Risks and test signals: ACL logic is security-sensitive, and several paths intentionally skip checks for internal multipart segment cleanup. Tests should cover each `ACL_MAP` entry, missing permissions, malformed ACL XML, mixed XML and headers, owner preservation, multipart tmpacl propagation, versionId query handling, and AccessDenied behavior.
