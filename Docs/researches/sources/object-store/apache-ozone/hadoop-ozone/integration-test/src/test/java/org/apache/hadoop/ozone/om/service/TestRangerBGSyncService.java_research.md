# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRangerBGSyncService.java

## Purpose
External-service integration tests for `OMRangerBGSyncService`, validating reconciliation between OM multitenancy metadata and Apache Ranger policies/roles/users. The class is marked unhealthy because it requires a configured Ranger endpoint.

## Important APIs and Types
The class uses `OMRangerBGSyncService`, `RangerClientMultiTenantAccessController`, `MultiTenantAccessController.Policy`, `Role`, `RangerUserRequest`, `OMMultiTenantManager`, `OmDBTenantState`, `OmDBAccessIdInfo`, `OMMetrics`, `OmMetadataManagerImpl`, `AuthorizerLockImpl`, `OzoneManagerRatisServer`, `AuditLogger`, `KerberosName`, and Mockito. Tests include `testRemovePolicyAndRole`, `testConsistentState`, `testRecoverRangerRole`, and `testRecreateDeletedRangerPolicy`.

## Control Flow
Static setup reads Ranger connection properties from JVM system properties and configures logging. Per-test setup builds a mocked `OzoneManager`, real local OM metadata DB, mocked Ratis server that writes Ranger service version to the meta table, Kerberos short-name rules, and a real Ranger access controller. Helper `createRolesAndPoliciesInRanger` optionally populates OM tenant/access-ID tables, creates test Ranger users, creates admin/user roles, and creates default tenant policies. Tests start the background sync service, wait for its run counter to advance, shut it down, then inspect Ranger and OM DB service versions.

## State and Persistence
State is split between local OM metadata tables and the external Ranger service. OM persistence includes tenant state, access ID rows, and `RANGER_OZONE_SERVICE_VERSION_KEY` in the meta table. Ranger persistence includes users, roles, and policies created and cleaned up around each test.

## Dependencies and Integration Points
The file integrates OM multitenancy desired-state generation, Ranger REST/client APIs, OM audit/metrics, Ratis-mediated meta-table writes, Kerberos user normalization, and Ranger cleanup helper calls.

## Risks and Edge Cases
Tests require real Ranger credentials and endpoint system properties. Cleanup is best-effort and logs errors rather than failing, so leaked Ranger resources are possible after partial failures. The companion `RangerUserRequest` globally relaxes HTTPS certificate validation. Exact Ranger error status codes are asserted for missing policy/role lookups.

## Test Signals
Signals include orphan Ranger policies/roles being deleted when no OM DB tenant exists, no Ranger writes for consistent desired state, tampered role membership being restored from OM DB access IDs, deleted tenant policies being recreated, and OM DB Ranger service version matching Ranger's policy version after sync.
