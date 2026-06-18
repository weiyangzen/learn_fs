# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestMultiTenantVolume.java

## Purpose
Mini-cluster integration tests for Ozone multitenancy volume routing, tenant API upgrade finalization gating, S3 secret compatibility, tenant quota behavior, Ranger service-version persistence, and tenant ID validation.

## Important APIs and Types
The class `TestMultiTenantVolume` uses `MiniOzoneCluster`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `RpcClient`, `S3Auth`, `OzoneManagerProtocol`, `UpgradeFinalization`, `OMLayoutFeature`, `OMMultiTenantManagerImpl`, `S3SecretValue`, `OzoneQuota`, and multitenancy object-store APIs such as `createTenant`, `tenantAssignUserAccessId`, `tenantRevokeUserAccessId`, `deleteTenant`, `getS3Volume`, and `createS3Bucket`.

## Control Flow
`@BeforeAll` starts an OM-only cluster with multitenancy enabled, Ranger skipped for dev tests, and initial OM layout version forced before multitenancy finalization. It runs `preFinalizationChecks`, which asserts tenant APIs fail before finalization while S3 secret APIs still work, then triggers OM upgrade finalization and waits for completion. Tests then create default or tenant-scoped object stores, set thread-local S3 auth access IDs, create buckets, revoke tenant users, delete tenants/volumes, and validate quota and ID behavior.

## State and Persistence
Persistent OM state includes tenant table entries, tenant volumes, S3 bucket metadata, access ID mappings, S3 secrets, meta-table Ranger service version, and quota fields on tenant volumes. The manually created `ObjectStore` carries S3 auth state in the `RpcClient` thread-local rather than through the default mini-cluster client.

## Dependencies and Integration Points
This integrates OM upgrade finalization, multitenant manager, S3 auth routing, object-store S3 bucket APIs, OM metadata tables, quota handling, and Ranger background sync version writes through Ratis.

## Risks and Edge Cases
The static cluster is shared across tests, so cleanup of tenants, buckets, and volumes matters. `getStoreForAccessID` constructs `RpcClient` instances without explicit close in this file. The default tenant ID strictness test assumes S3-compliant naming is enabled by default and checks message content for underscores.

## Test Signals
Signals include tenant APIs blocked before finalization, S3 secret APIs still available before finalization, non-tenant S3 requests routed to the default S3 volume, tenant access ID requests routed to the tenant volume, other users not seeing tenant buckets, Ranger service version persisted in OM metadata, tenant volume quotas set/read correctly, and invalid tenant IDs rejected.
