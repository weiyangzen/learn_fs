# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/s3_acl.py

Purpose: Implements S3 ACL subresource behavior for the full `s3_acl` mode where ACLs are stored as Swift sysmeta and represented by `subresource.ACL`.

Important APIs and control flow: `S3AclController.GET` HEADs the object or bucket, selects `resp.object_acl` or `resp.bucket_acl`, serializes `acl.elem()` to XML, and returns OK. `PUT` updates object ACLs by issuing a self-copy with `X-Copy-From` and zero content length because object sysmeta cannot be changed by POST; bucket ACLs are updated via Swift `POST`. ACL parsing and permission enforcement are performed by `S3AclHandler` before controller execution.

State, dependencies, and integration: Persistent ACL state lives in object or container sysmeta encoded by the request/response layer. It depends on URL quoting for self-copy paths, XML serialization, and ACL handlers to set `req.object_acl` or `req.bucket_acl`.

Risks and test signals: Object ACL updates rely on copy semantics and can interact with object metadata, versioning, or large-object behavior. Tests should cover GET bucket/object ACL XML, PUT bucket ACL POST, PUT object ACL self-copy headers, quoted object names, and handler rejection before mutation.
