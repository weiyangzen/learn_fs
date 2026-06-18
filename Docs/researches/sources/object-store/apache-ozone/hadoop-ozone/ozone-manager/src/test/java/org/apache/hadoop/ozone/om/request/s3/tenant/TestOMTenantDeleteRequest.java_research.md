# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestOMTenantDeleteRequest.java

Purpose: tests ACL-denied pre-execute behavior for `OMTenantDeleteRequest`. The class focuses on authorization failure rather than full tenant deletion success.

Important APIs and types: `OMTenantDeleteRequest`, `OMMultiTenantManager`, `OzoneTenant`, `OmDBTenantState`, `TenantOp`, `AuthorizerLock`, `OMRequestTestUtils.deleteTenantRequest`, `OMException`, `OzoneObj`, and `IAccessAuthorizer`.

Control flow: setup configures a mocked `OzoneManager`, real metadata manager and metrics, layout version manager, audit logger, and multi-tenant manager that reports tenants empty and returns an `OzoneTenant`. The test enables ACLs, creates a tenant state row in the tenant-state table, builds a delete request, and instantiates an anonymous `OMTenantDeleteRequest` whose `checkAcls` throws `PERMISSION_DENIED`. It then asserts `preExecute` throws that result.

State and persistence behavior: the test seeds `tenantStateTable` with `OmDBTenantState` so pre-execute has realistic tenant metadata available. Because the failure happens during pre-execute, no deletion cache/table mutation should occur.

Dependencies and integration points: models the interaction among tenant metadata, multi-tenant manager emptiness checks, authorizer locks, tenant operations, and OM ACL enforcement. External authorizer/cache operations are mocked as no-op.

Risks covered: tenant deletion bypassing ACL checks when ACLs are enabled, or permission failures being converted to wrong exception types. It does not validate successful delete cleanup or non-empty tenant errors.

Test signals: `assertThrows(OMException.class)` from `preExecute` and result code `PERMISSION_DENIED`.
