<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/SharedTmpDirAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/SharedTmpDirAuthorizer.java

Purpose: Hybrid authorizer that forces OFS shared temporary bucket access checks through native ACLs while delegating all other objects to a configured custom authorizer.

Important APIs/types/functions: Constructor accepts an `OzoneNativeAuthorizer` and a delegate `IAccessAuthorizer`. `checkAccess` checks nulls, detects `OzoneObjInfo`, calls `OFSPath.isSharedTmpBucket`, and chooses native or delegate authorizer.

Control flow: For shared tmp bucket objects, access is evaluated by the native authorizer. For non-shared-tmp objects or non-`OzoneObjInfo` implementations, the configured authorizer handles the request.

State and persistence behavior: No persistence. Holds two authorizer references.

Dependencies and integration points: Created by `OzoneAuthorizerFactory` when a non-native authorizer is configured and shared tmp support is enabled. Depends on `OFSPath` shared tmp detection.

Risks: Shared tmp detection only runs for `OzoneObjInfo`; custom `IOzoneObj` implementations bypass the native special case. The wrapper assumes the native authorizer has been configured with the same OM managers.

Test signals: Tests should verify native delegation for shared tmp, custom delegation for ordinary buckets/keys, null argument failures, and behavior for non-`OzoneObjInfo` objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/SharedTmpDirAuthorizer.java -->
