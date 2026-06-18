# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/acl.py

Purpose: Implements legacy/non-`s3_acl` S3 ACL subresource support by deriving S3 ACL XML from Swift container ACL headers and translating bucket ACL writes into Swift POSTs.

Important APIs and control flow: `get_acl` builds an `AccessControlPolicy` XML document granting the account full control, then uses Swift ACL parsing and referrer checks to add AllUsers READ or WRITE grants when `x-container-read` or `x-container-write` allows public access. `AclController.GET` HEADs the target resource and returns generated ACL XML. `AclController.PUT` rejects object ACL updates as unimplemented, validates that exactly one of `x-amz-acl` or ACL XML body is present, translates XML ACLs through `swift_acl_translate`, issues a Swift `POST`, forces status 200, and sets `Location` to the bucket name.

State, dependencies, and integration: No persistent state. It depends on Swift ACL parsing, s3api XML builders, and request helpers for body parsing and Swift response translation.

Risks and test signals: This path cannot represent full S3 ACL semantics, especially object ACLs. Tests should cover public-read/write derivation, missing security header, unexpected content when both header and XML exist, malformed XML, object PUT unimplemented, and response status/location normalization.
