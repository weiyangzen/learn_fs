# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestAssumeRoleRequest.java

Purpose: tests `AssumeRoleRequest` and nested `OzoneGrant` value semantics, getters, immutability of S3 actions, and equality/hash behavior.

Important APIs/types/functions: exercises `AssumeRoleRequest` constructor, getters for host/IP/client UGI/target role/grants, `OzoneGrant` getters for objects/permissions/S3 actions, and `equals/hashCode`.

Control flow and state: builds bucket `OzoneObjInfo` targets, ACL permission sets, and grants with empty or populated S3 action sets. Tests assert two equivalent requests compare equal, target role differences compare unequal, S3 action sets are unmodifiable, and grants/requests with S3 actions differ from those without.

Dependencies and integration points: uses `UserGroupInformation`, `OzoneObjInfo`, `IAccessAuthorizer.ACLType`, and Java set implementations. It represents IAM/S3 assume-role authorization input.

Risks and test signals: catches mutable grant action exposure and equality omissions for S3 actions. Correct value semantics are important for policy caching, deduplication, and audit comparisons.
