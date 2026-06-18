<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAuthorizerFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAuthorizerFactory.java

Purpose: Factory for OM and snapshot access authorizers based on OM configuration.

Important APIs/types/functions: `forOM` creates an authorizer for the live OM managers. `forSnapshot` returns a fresh authorizer for snapshot managers when the active authorizer is native, otherwise reuses the configured non-native authorizer. `createImpl` chooses no-op, native, custom `OzoneManagerAuthorizer`, plain custom `IAccessAuthorizer`, or `SharedTmpDirAuthorizer`. `authorizerClass` reads `OZONE_ACL_AUTHORIZER_CLASS`.

Control flow: If ACLs are disabled or the configured class is `OzoneAccessAuthorizer`, it returns the singleton no-op authorizer. Native authorizer is configured with OM managers. Custom OM-aware authorizers receive `configure`. For other custom authorizers, the factory optionally wraps them with native handling for OFS shared tmp when that feature is enabled.

State and persistence behavior: No persistence. It creates or reuses authorizer instances and logs the selected class.

Dependencies and integration points: Integrates `OzoneManager`, `OmSnapshot`, key/prefix managers, ACL config, reflection-based instantiation, and shared tmp directory policy.

Risks: Reflection errors surface during OM startup/configuration. Reusing non-native authorizers for snapshots assumes they can handle snapshot contexts. Shared tmp wrapping changes behavior only for non-native authorizers, so native/custom parity depends on config.

Test signals: Tests should cover ACL-disabled no-op, native configuration, custom `OzoneManagerAuthorizer` configuration, plain custom wrapping when shared tmp is enabled, and snapshot authorizer reuse versus recreation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAuthorizerFactory.java -->
