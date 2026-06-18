
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMTenantAssignAdminRequest.java

Purpose: Grants tenant admin status to an existing tenant access ID and records whether the admin is delegated.

Important APIs and types: Extends `OMClientRequest`; uses `TenantAssignAdminRequest/Response`, `OmDBAccessIdInfo`, `OMMultiTenantManager`, Ranger authorizer operations, `tenantAccessIdTable`, and `VOLUME_LOCK`.

Control flow: `preExecute` resolves a missing tenant ID from the access ID, checks tenant existence and tenant-admin privilege, verifies the access ID exists and belongs to the tenant, defaults `delegated` to true, takes the authorizer write lock, calls Ranger `assignTenantAdmin`, and rewrites the request with resolved fields. `validateAndUpdateCache` locks the tenant volume, reloads the access record, writes a new `OmDBAccessIdInfo` with admin flags, updates the multi-tenant cache, returns a response, releases both locks, audits, and increments failure metrics on error.

State and persistence behavior: Updates the tenant access ID table cache only; user-principal and S3-secret tables are unchanged. Ranger role membership is modified before Ratis DB mutation and guarded by the authorizer lock.

Dependencies and integration points: Integrates tenant CLI/API admin operations with OM DB, in-memory tenant cache, metrics, audit logging, and Ranger role changes.

Risks: Ranger side effects can happen before OM cache update failure, so background reconciliation must handle divergence. Assertions enforce tenant match in validation but production safety relies on preExecute checks. Tests should cover implicit tenant resolution, delegated defaulting, mismatched access ID, missing access ID, and failure cleanup/lock release.
