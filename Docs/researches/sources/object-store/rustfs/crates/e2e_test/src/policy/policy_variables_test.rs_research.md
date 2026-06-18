# sources/object-store/rustfs/crates/e2e_test/src/policy/policy_variables_test.rs

Purpose: ignored full-E2E tests for AWS IAM policy variable substitution in RustFS authorization. The suite covers `${aws:username}` in single resources, multiple resources, concatenated strings, nested variable syntax, STS-style users, and explicit deny precedence.

Important APIs/types/functions: helpers `create_user`, `create_sts_user`, `create_and_attach_policy`, and `cleanup_user_and_policy` call RustFS admin APIs with `awscurl_put`/`awscurl_delete`. Each scenario has an ignored `#[tokio::test]` entry, a standalone `_impl`, and an `_impl_with_env` variant used by `PolicyTestSuite`. Tests create S3 clients with user credentials through `PolicyTestEnvironment`.

Control flow: each implementation creates a user and canned policy, attaches it, optionally waits briefly for propagation, performs allowed and denied S3 operations, then best-effort cleans up buckets, objects, user, and policy. Single-value tests allow bucket/object access under `${aws:username}-*` and deny unrelated bucket creation. Multi-value tests allow exactly three username-derived bucket names. Concatenation allows `prefix-${aws:username}-suffix`. Nested tests expect `arn:aws:s3:::${${aws:username}-test}` to resolve to `<user>-test` and reject unresolved variable strings. STS tests currently create a regular user via `create_sts_user` and validate `${aws:username}-sts-bucket` access. Deny tests combine allow rules with a deny on `*private*` and expect deny to win.

State and persistence behavior: creates persistent RustFS admin users and canned policies on an existing server at `127.0.0.1:9000`. Cleanup deletes known bucket patterns and admin resources, but is best-effort and only runs after certain error branches, so interrupted tests can leave state behind. The environment itself only removes a temp directory on drop and does not stop the server.

Dependencies and integration points: depends on shared admin curl helpers, AWS S3 SDK, `PolicyTestEnvironment`, `serial_test`, and RustFS admin routes `/rustfs/admin/v3/add-user`, `/add-canned-policy`, `/set-user-or-group-policy`, `/remove-user`, and `/remove-canned-policy`. It integrates IAM policy evaluation with S3 `ListBuckets`, `CreateBucket`, `ListObjectsV2`, `PutObject`, and `GetObject`.

Risks: all direct tests are ignored and assume an external RustFS server rather than starting one. Fixed usernames and policy names can collide with stale state. The STS path is only a regular-user approximation, not a real AssumeRole/temporary-credential flow. Nested variable behavior may be nonstandard and should be checked against intended policy semantics. Cleanup misses some object keys if tests add new keys.

Test signals: good authorization regression signals for variable expansion in resource ARNs, multi-resource matching, concatenation, deny precedence, and user-scoped bucket/object permissions when run in full E2E mode.
