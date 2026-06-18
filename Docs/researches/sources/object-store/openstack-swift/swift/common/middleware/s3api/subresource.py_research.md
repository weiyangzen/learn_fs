<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/subresource.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/subresource.py

## Purpose
Implements S3 ACL subresource data structures and conversions. It translates between S3 ACL XML/header models and compact JSON stored in Swift sysmeta, defines canonical users and predefined groups, and checks owner/permission access when S3 ACL enforcement is enabled.

## Important APIs, types, and functions
`encode_acl(resource, acl)` writes ACL JSON to `x-*-sysmeta-s3api-acl`; `decode_acl(resource, headers, allow_no_owner)` reconstructs an `ACL`. `Grantee`, `User`, `Group`, `AuthenticatedUsers`, `AllUsers`, and `LogDelivery` model S3 grantees. `Grant` pairs a grantee with a permission. `ACL` serializes XML, parses XML with `from_elem`, builds ACLs from request headers with `from_headers`, and enforces `check_owner`/`check_permission`. `canned_acl` and `ACLPrivate`/`ACLPublicRead`/... produce AWS canned ACLs.

## Control flow
Incoming ACL XML is parsed into owner and grants. Incoming grant headers are parsed by `Grantee.from_header`; canned ACLs expand through `canned_acl_grantees`. Supplying both canned ACL and explicit grant headers raises `InvalidRequest`. ACL persistence encodes owner id and grant tuples as JSON. Permission checks first bypass enforcement when `s3_acl` is false, then allow owners full control, then scan grants for `FULL_CONTROL` or the requested permission.

## State and persistence behavior
The persistent representation is a JSON object with `Owner` and `Grant` entries stored in Swift sysmeta. In-memory `ACL` instances hold owner, grant list, `s3_acl`, and `allow_no_owner` flags. `allow_no_owner` can make missing owner metadata effectively public for compatibility. `LogDelivery` membership is derived from the user portion of the Swift user id and the `.log_delivery` marker.

## Dependencies and integration points
Used by `s3request` ACL properties and `S3AclRequest.get_acl_response`, and by ACL controllers/handlers. It depends on S3 XML helpers, S3 response errors, `sysmeta_header`, Swift JSON utilities, and `InvalidSubresource` for corrupt stored ACLs. It also interacts with bucket logging through the `LogDelivery` predefined group.

## Risks and test signals
Risks include overly broad public access because `AllUsers` and `AuthenticatedUsers` both return true in this signed-request model, no support for email grantees, malformed or legacy sysmeta causing `InvalidSubresource`, and permission strings outside the fixed set raising not implemented. Tests should cover canned ACL expansion, explicit grant headers, conflict between canned and explicit grants, XML parse/render, encode/decode round trip, corrupt JSON handling, owner bypass, missing-owner compatibility, and log-delivery membership.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/subresource.py -->
