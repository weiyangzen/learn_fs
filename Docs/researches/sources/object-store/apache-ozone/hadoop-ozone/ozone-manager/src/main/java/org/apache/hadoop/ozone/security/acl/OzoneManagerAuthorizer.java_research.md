<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneManagerAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneManagerAuthorizer.java

Purpose: OM-specific extension of `IAccessAuthorizer` for authorizers that need OM manager dependencies.

Important APIs/types/functions: Declares `configure(OzoneManager om, KeyManager km, PrefixManager pm)` returning an `OzoneManagerAuthorizer`.

Control flow: The factory detects implementations of this interface and calls `configure` after reflective construction. Native authorizer implements this path.

State and persistence behavior: No state in the interface. Implementations may retain manager references to read ACL metadata.

Dependencies and integration points: Depends on `OzoneManager`, `KeyManager`, and `PrefixManager`. Used by `OzoneAuthorizerFactory`.

Risks: Implementations must be safe to configure once and then use concurrently. Returning the wrong instance or failing to retain dependencies will break access checks at runtime.

Test signals: Factory tests should verify `configure` is invoked and its returned instance is used.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneManagerAuthorizer.java -->
