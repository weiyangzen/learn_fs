# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantCreateRequest.java

Purpose: tests `OMTenantCreateRequest`, including happy-path tenant/volume creation, existing-volume force flag behavior, S3-compliant tenant ID validation under strict S3 mode, non-strict acceptance, and ACL-denied pre-execute behavior.

Important APIs and types: `OMTenantCreateRequest`, `CreateTenantRequest`, `OMMultiTenantManager`, `TenantOp`, `AuthorizerLock`, `OMLayoutVersionManager`, `OMRequestTestUtils.createTenantRequest`, `OMException`, `Status`, `OzoneObj`, and `IAccessAuthorizer`.

Control flow: setup creates a mocked `OzoneManager`, real metadata manager, metrics, layout version manager that allows features, audit logger, and mocked multi-tenant manager with no-op admin/authorizer/cache operations. Happy path spies the request to return username, pre-executes, validates, and checks response/table. Existing-volume test seeds volume table, verifies `preExecute` throws when force is false, succeeds when force is true, then crafts a post-preExecute request with force false to test validate-time `VOLUME_ALREADY_EXISTS`.

State and persistence behavior: successful tenant creation creates a volume table entry for the tenant ID and returns `CreateTenantResponse`. Existing volume with force true allows tenant creation over the pre-existing volume. Strict S3 validation happens during pre-execute via volume-name constraints.

Dependencies and integration points: integrates with multi-tenant admin checks, authorizer locks, Ranger/tenant operations, OM layout feature gating, audit logging, max user volume count, and ACL checks. ACL test subclasses `checkAcls` to throw `PERMISSION_DENIED` when ACLs are enabled.

Risks covered: bypassing existing-volume safeguards, rejecting valid S3 names, accepting invalid names in strict mode, ignoring ACL denial, and failing to create required volume state. The tests mock external tenant/Ranger operations rather than validating side effects there.

Test signals: response contains `CreateTenantResponse`, status `OK` or `VOLUME_ALREADY_EXISTS`, volume table entry exists after success, exception result `VOLUME_ALREADY_EXISTS` or `PERMISSION_DENIED`, and strict-mode invalid-name message.
