# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TenantOp.java

Purpose: `TenantOp` defines the private, unstable interface for authorizer-side multi-tenant operations, primarily Ranger role and policy management plus tenant user/admin assignment.

Important APIs and types: Methods are `createTenant`, `deleteTenant`, `assignUserToTenant`, `revokeUserAccessId`, `assignTenantAdmin`, and `revokeTenantAdmin`. It depends on the multi-tenant `Tenant` model and throws `IOException`.

Control flow: The interface has no implementation. Concrete authorizer integrations perform external side effects such as creating or deleting Ranger roles and policies and updating privileges for access IDs.

State and persistence behavior: State is external to OM DB and typically held in Ranger or another authorizer. OM request handlers must coordinate this external state with OM's tenant tables.

Dependencies and integration points: It is the bridge from OM tenant metadata operations to the authorization backend.

Risks and test signals: Distributed consistency is the central risk: Ranger updates and OM DB updates may fail independently. Tests should cover idempotent create/delete, rollback or retry behavior, missing access IDs, delegated admin semantics, and exception mapping from the authorizer.
