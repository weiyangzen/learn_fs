# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/RequestContext.java

Purpose: Immutable authorization context carrying caller identity, network address, requested ACL right, owner, recursive flag, STS session policy, and S3 action.

Important APIs and types: Fields include host, IP, client UGI, service ID, ACL identity type, ACL right, owner name, recursive-access flag, session policy, and S3 action. `Builder` provides setters, `build`, and a getter for current ACL right; `toBuilder` clones a context.

Control flow: Callers assemble contexts with `RequestContext.newBuilder()`. Authorizers read fields to decide access. `toBuilder` copies every field for mutation.

State and persistence behavior: In-memory per-request object. Session policy string can be a serialized authorization policy produced by `generateAssumeRoleSessionPolicy`; this class does not parse or persist it.

Dependencies and integration points: Used by all `IAccessAuthorizer.checkAccess` implementations, recursive prefix checks, owner privilege logic, Ranger STS session policy handling, and S3 Gateway action restrictions.

Risks: Builder performs no validation, so null ACL rights, UGI, or owner can reach authorizers. Session policy and S3 action are plain strings; format validation is provider-specific. Recursive flag has meaning only when the target object is directory-like.

Test signals: Verify builder/toBuilder field preservation, authorizer behavior for missing optional fields, recursive check behavior, and STS/S3 action propagation.
