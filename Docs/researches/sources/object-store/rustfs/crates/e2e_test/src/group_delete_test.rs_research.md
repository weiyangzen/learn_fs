<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/group_delete_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/group_delete_test.rs

Purpose: this module contains ignored, real-server E2E regression tests for RustFS group management around issue #2028. It verifies group deletion rules, propagation of group-attached policies to users without explicit user policies, and cache/backend consistency after deleting a group member user.

Important APIs, types, and functions: `create_user_s3_client()` builds an AWS SDK S3 client for a created IAM user. Tests call admin endpoints through `awscurl_put()`, `awscurl_delete()`, and `awscurl_get()`: `/add-user`, `/update-group-members`, `/set-user-or-group-policy`, `/group/{name}`, `/group?group=...`, and `/remove-user`.

Control flow: `test_delete_group_requires_empty_membership()` creates a user, adds it to a group, asserts deleting the non-empty group fails, removes the member, deletes the empty group, and verifies lookup fails. `test_user_with_only_group_gets_group_policies()` creates a canned ListAllMyBuckets policy, creates a user with no direct policy, adds the user to a group, attaches the policy to that group, and confirms the user can list buckets. `test_delete_group_after_deleting_user()` creates a sole member, deletes the user, then verifies deleting the now-empty group succeeds.

State and persistence: the tests mutate IAM users, groups, group membership indexes, group policy attachments, and cached membership state inside a temporary RustFS server. They do not perform comprehensive cleanup because each test uses isolated server state, but names are static inside the module and require serial execution.

Dependencies and integration points: depends on `RustFSTestEnvironment`, awscurl admin helpers, AWS SDK S3 list-buckets, and `serial_test`. The tests integrate directly with RustFS admin API semantics, group membership persistence, policy evaluation, and any in-memory membership cache.

Risks: all tests are `#[ignore]`, so normal `cargo test` will not run them. Static user/group/policy names are safe only because the environment is isolated and tests are serial. The group-policy test asserts one positive action but not negative controls for unauthorized actions. Failure paths can leave admin state alive until environment cleanup.

Test signals: useful signals are non-empty group deletion rejection, empty group deletion success, failed group lookup after deletion, group-only user authorization through group policy, and successful group deletion after deleting the sole member without stale-cache rejection.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/group_delete_test.rs -->
