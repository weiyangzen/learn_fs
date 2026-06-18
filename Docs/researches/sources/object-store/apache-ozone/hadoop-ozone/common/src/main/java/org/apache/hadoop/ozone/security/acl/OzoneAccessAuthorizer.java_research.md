# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneAccessAuthorizer.java

Purpose: No-op native `IAccessAuthorizer` implementation that allows every access check.

Important APIs and types: Singleton instance returned by `get`; `checkAccess` always returns true; `isNative` returns true.

Control flow: No branching beyond returning the singleton and unconditional authorization.

State and persistence behavior: Stateless singleton. It does not read ACL metadata or persist decisions.

Dependencies and integration points: Used when ACL enforcement is disabled or when a permissive native authorizer is configured. It satisfies code paths that require an authorizer instance.

Risks: If accidentally configured in a secured deployment, all ACL checks pass. Its `isNative` true can affect code that treats native authorizers specially even though it is permissive.

Test signals: Verify singleton identity, unconditional success, and configuration tests that distinguish permissive authorizer from enforcing native/Ranger authorizers.
