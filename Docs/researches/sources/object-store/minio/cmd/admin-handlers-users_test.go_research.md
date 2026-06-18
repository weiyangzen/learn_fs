# sources/object-store/minio/cmd/admin-handlers-users_test.go

## Purpose
`admin-handlers-users_test.go` is the primary black-box integration test suite for MinIO admin IAM handlers. It starts real MinIO test servers across backend variants, drives madmin and S3 clients, and verifies that users, groups, policies, service accounts, plugin authorization, and selected privilege-escalation regressions behave as intended for the internal IDP.

## Important APIs, Types, And Functions
The central fixture is `TestSuiteIAM`, embedding `TestSuiteCommon` and holding endpoint, admin client, S3 client, backend description, and etcd-backend flag. Setup helpers include `newTestSuiteIAM`, `iamSetup`, `setUpEtcd`, `SetUpSuite`, `RestartIAMSuite`, `getAdminClient`, and `getUserClient`. `iamTestSuites` constructs the backend matrix: ErasureSD, ErasureSD TLS, Erasure, and ErasureSet, each with and without etcd.

Top-level suites are `TestIAMInternalIDPServerSuite` and `TestIAM_AMPInternalIDPServerSuite`. Test methods include `TestUserCreate`, `TestUserPolicyEscalationBug`, `TestAddServiceAccountPerms`, `TestPolicyCreate`, `TestCannedPolicies`, `TestGroupAddRemove`, `TestServiceAccountOpsByUser`, `TestServiceAccountDurationSecondsCondition`, `TestServiceAccountOpsByAdmin`, `TestServiceAccountPrivilegeEscalationBug`, `TestServiceAccountPrivilegeEscalationBug2_2025_10_15`, `SetUpAccMgmtPlugin`, and `TestAccMgmtPlugin`.

Assertion helpers cover IAM user creation/info negative checks, service-account create/list/info/session-policy/secret/status/delete, S3 list/upload/download/delete expectations, object tag/head/version helpers, and random credential generation.

## Control Flow
`TestIAMInternalIDPServerSuite` skips Windows, then runs every IAM scenario against every suite variant. Setup may configure etcd using `_MINIO_ETCD_TEST_SERVER`, restart the IAM suite, and rebuild clients. Each test uses a context with a 30-second timeout.

`TestUserCreate` covers create/list, policy attach, S3 access, secret-key update invalidating old credentials, disable/enable effects, and deletion invalidating credentials. `TestUserPolicyEscalationBug` crafts a signed raw `add-user` request as the user being updated and verifies the user cannot gain consoleAdmin-like bucket deletion despite receiving HTTP 200 for password/status update behavior.

Policy tests add valid and invalid JSON policies, attach them to users, prove exact S3 permissions, verify default policy presence, allow overwriting `readwrite`, reject comma-containing policy names, and reject deleting a policy still attached to a user.

Group tests create a user and group, attach a policy to the group, verify list/get group details, disable and re-enable group access, reject deleting a non-empty group, remove the member, and finally delete the empty group.

Service-account tests split admin-created and user-created flows. They verify service accounts appear in listing, info reports parent/status/implied policy, S3 access works, session policy can restrict and later allow access, secret-key updates invalidate old credentials, status updates disable access, deletion invalidates credentials, and non-admin users cannot create accounts for other users. The duration-condition test verifies `svc:DurationSeconds` policy evaluation by allowing a 30-minute service account and rejecting a two-hour one.

Privilege escalation tests create restricted service accounts for root and regular users, then verify they cannot update their own policy to full S3 access and cannot create broader service accounts bypassing their sub-policy. The access-management-plugin suite configures the policy plugin from `_MINIO_POLICY_PLUGIN_ENDPOINT`, restarts, verifies plugin-denied object upload, verifies service-account admin flows under plugin authorization, and confirms session policies are ignored when enforcement is delegated to the plugin.

## State And Persistence Behavior
The tests create real IAM users, canned policies, groups, service accounts, buckets, and objects in each temporary test server. When etcd is configured, IAM state is persisted through a unique etcd path prefix and the server is restarted to use that backend. Many assertions validate state transitions by performing S3 operations with old and new credentials rather than only inspecting admin responses.

The suite exercises both high-level admin state (`ListUsers`, `ListGroups`, `InfoServiceAccount`) and authorization side effects (bucket list, put, delete, old secret invalidation, disabled account denial). It uses server teardown for most cleanup, with some privilege-regression tests using defers for explicit bucket/user/service-account cleanup.

## Dependencies And Integration Points
The test file depends on `madmin-go/v3`, `minio-go/v7`, static V4 credentials, request signing, S3 URL encoding utilities, MinIO auth credential generation, environment variables for etcd and policy plugin, and shared test server infrastructure. It tests the HTTP handlers in `admin-handlers-users.go` through official admin clients plus a few raw signed requests.

The plugin suite integrates with the example external access-management plugin contract, assuming it denies `s3:Put*` for non-root accounts. The service-account assertions integrate admin API behavior with actual S3 authorization to catch policy-evaluation bugs.

## Risks And Test Signals
The suite is broad but expensive because it multiplies scenarios by backend and optional etcd variants. It skips Windows, so Windows-specific IAM behavior is not covered here. Plugin and etcd paths are conditional on environment variables, which means those important modes may be skipped in ordinary local runs.

Strong signals include credential invalidation after password update, disabled/deleted user denial, invalid policy rejection, attached-policy delete rejection, group disable revoking access, service-account session-policy enforcement, `svc:DurationSeconds` condition enforcement, access-management-plugin delegation, and explicit privilege escalation regressions. Missing coverage in this file includes IAM import/export, token revocation, LDAP-specific workflows, OpenID bulk listing, and site-replication hook verification.
