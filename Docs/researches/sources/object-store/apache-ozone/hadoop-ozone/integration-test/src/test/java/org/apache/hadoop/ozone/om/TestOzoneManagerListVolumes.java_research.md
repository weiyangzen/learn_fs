# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumes.java

## Purpose
Abstract non-HA integration test for `ObjectStore.listVolumesByUser` and `listVolumes` under ACL-enabled/disabled and `ozone.om.volume.listall.allowed` combinations.

## Important APIs, types, and functions
- Implements `NonHATests.TestCase` and uses `cluster().newClient()` from the test harness.
- Uses `ObjectStore`, `ClientProtocol.setVolumeOwner`, `OzoneObjInfo`, `OzoneAcl.parseAcls`, and UGI login switching.
- Helper `checkUser` validates both user-scoped listing and list-all behavior with expected permission failures.

## Control flow
`@BeforeAll` creates five uniquely prefixed volumes as admin, assigns owners user1/user2, and sets ACLs so some volumes are owner-accessible, some cross-user accessible, and one world-accessible. Each test switches login UGI and configures `setListAllVolumesAllowed`, then checks expected visible volumes and whether list-all should succeed. Parameterized tests cover ACL-disabled behavior for both list-all settings.

## State and persistence behavior
The suite persists volume ownership and ACLs in OM metadata. It mutates in-memory OM config `listAllVolumesAllowed` per test and restores the default in `@AfterEach`. Login user state is also reset after each test.

## Dependencies and integration points
It integrates non-HA MiniOzoneCluster harnesses, client volume APIs, ACL parsing/authorization, UGI identity/short-name behavior, config assumptions for ACL-enabled mode, and default `s3v` volume visibility.

## Risks and edge cases
The tests are conditional via `assumeConfig`, so coverage depends on the cluster's ACL config. Runtime exceptions wrap `OMException`, and the helper must preserve unexpected causes. Expected lists include ACL-derived access rather than exact full listing except for count/list-all checks.

## Test signals
Signals include accessible volume sets containing expected names, exact count of five prefixed volumes for list-all, `PERMISSION_DENIED` for disallowed non-admin list-all/list-other-user cases, and successful short-name handling for a Kerberos-style username.
