
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantRevokeAdminRequest.java

Purpose: Removes tenant admin status from an access ID while leaving the user assigned to the tenant.

Important APIs and types: Extends `OMClientRequest`; uses `TenantRevokeAdminRequest/Response`, `OmDBAccessIdInfo`, `OMMultiTenantManager`, Ranger `revokeTenantAdmin`, `tenantAccessIdTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` resolves tenant ID from access ID when absent, validates tenant existence/admin privilege, verifies the access ID exists and belongs to the tenant, takes the authorizer write lock, and removes the user from the Ranger admin role. Validation locks the tenant volume, reloads the access ID row, replaces it with admin/delegated flags set false, updates the tenant cache, builds the response, releases locks, audits, and records failure metrics.

State and persistence behavior: Writes a new tenant access ID table cache value at the transaction index. It does not modify principal mappings or secrets.

Dependencies and integration points: Integrates tenant authorization, Ranger admin roles, OM access ID metadata, metrics, and audit logging.

Risks: Ranger mutation before DB mutation can leave temporary divergence. The handler uses `assert` for tenant match in validation. Tests should cover inferred tenant ID, missing access ID, non-admin revocation idempotence expectations, and lock release on Ranger/DB errors.
