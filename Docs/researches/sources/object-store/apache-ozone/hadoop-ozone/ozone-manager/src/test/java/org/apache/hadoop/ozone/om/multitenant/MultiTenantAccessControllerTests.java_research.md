# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessControllerTests.java

Purpose: abstract conformance suite for `MultiTenantAccessController` implementations, covering Ranger-style policy and role lifecycle behavior without binding to one concrete backend.

Important APIs/types: `MultiTenantAccessController`, nested `Policy`, `Role`, and `Acl` builders, `ACLType`, and `OMMultiTenantManager.OZONE_TENANT_RANGER_ROLE_DESCRIPTION`. Subclasses supply `createSubject()`.

Control flow: setup initializes test users and obtains the controller, skipping via AssertJ assumptions if policy version access is unavailable. Policy tests create, read, update, label-query, duplicate-check, and delete policies. Role tests create, duplicate-check, update membership, and delete roles. Policy-with-role tests assert creating a policy can create a referenced role and that later policy creation does not overwrite existing role users. ACL conversion tests generate all `ACLType` values except `NONE` and verify round-trip conversion through the controller.

State and persistence behavior: state lives in the controller backend. The suite expects service policy version increments after create/delete operations, persistent policy/resource uniqueness, role IDs assigned by backend, role user maps with delegation flags, and cleanup by explicit deletes.

Dependencies and integration points: integrates with Ranger-compatible policy concepts, Ozone ACL types, tenant roles, and subclasses such as the in-memory controller test. Uses JUnit 5, AssertJ, and Java collections.

Risks: because this is abstract, real backend behavior may be skipped if policy version access throws. Tests assume users `om` and `hdfs` exist for real Ranger clusters. Cleanup failures can leave backend state in non-in-memory runs.

Test signals: verifies CRUD, duplicate rejection, label filtering, policy version bumps, role preservation, role IDs, user membership mutation, and ACL string compatibility.
