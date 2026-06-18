<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAuthorizer.java

Purpose: Native OM ACL authorizer that evaluates Ozone volume, bucket, key, and prefix ACLs using OM manager metadata and admin/blacklist predicates.

Important APIs/types/functions: Implements `OzoneManagerAuthorizer`. `checkAccess(IOzoneObj, RequestContext)` is the core evaluator. `configure` wires volume, bucket, key, prefix managers and OM predicate methods. Setters allow tests to replace admin and blacklist checks. `isNative` returns true.

Control flow: `checkAccess` requires `OzoneObjInfo` and `RequestContext`, denies fully blacklisted users and read-blacklisted users for read/list ACLs, allows admins, allows read-only admins for read/list ACLs, allows owner access, handles list-all-volumes via config, computes parent ACL rights, then checks managers based on resource type. Volume creation is denied unless admin. Bucket/key/prefix creation skips checking the object being created but still checks parent access.

State and persistence behavior: The authorizer itself persists nothing. It reads ACL state through manager `checkAccess` calls and uses OM config for list-all-volumes permission.

Dependencies and integration points: Integrates with `VolumeManager`, `BucketManager`, `KeyManager`, `PrefixManager`, `OzoneAclUtils.getParentNativeAcl`, `OzoneAdmins`, `OzoneBlacklist`, and OM user predicates.

Risks: Owner bypass uses short username equality with `ownerName`; mismatches in Kerberos principal normalization can change access. CREATE semantics deliberately skip child object checks, so parent checks are critical. Non-`OzoneObjInfo` objects fail with `INVALID_REQUEST`. `allowListAllVolumes` can expose volume listing broadly if configured.

Test signals: Tests should cover blacklist precedence over admin-like rights, read-only admin scope, owner bypass, list-root behavior, create versus non-create access for each resource type, parent ACL requirements, and invalid object types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAuthorizer.java -->
