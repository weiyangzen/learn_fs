<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/existing_object_tag_policy_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/existing_object_tag_policy_test.rs

Purpose: this E2E module verifies IAM, bucket-policy, and STS session-policy evaluation for `s3:ExistingObjectTag` conditions, plus per-key authorization for `DeleteObjects`. It starts a real RustFS server, uses admin APIs through signed `awscurl`, creates temporary users/policies/buckets, and checks that tag changes immediately affect `GetObject` authorization.

Important APIs, types, and functions: `user_client()` and `sts_session_client()` build path-style AWS SDK S3 clients with static or session credentials. `assume_role_with_session_policy()` posts form-encoded STS `AssumeRole` requests through `awscurl_post_sts_form_urlencoded()`, then `parse_assume_role_credentials()` extracts temporary credentials from XML. Admin helpers wrap `/rustfs/admin/v3/add-user`, `/add-canned-policy`, `/set-user-or-group-policy`, and delete endpoints. Object helpers set initial tags through `PutObject.tagging()` and mutate tags through `PutObjectTagging`.

Control flow: each `#[tokio::test]` initializes logging, skips when `awscurl` is unavailable, starts `RustFSTestEnvironment`, creates unique names with `Uuid`, applies identity or bucket/session policy JSON, writes tagged objects, verifies allowed reads, flips `security=public` to `security=private`, and asserts denial. The delete-objects regression creates two keys, assumes a session with an allowed-prefix `s3:DeleteObject` policy, calls one `DeleteObjects` request containing both keys, and validates one `Deleted` entry plus one `AccessDenied` error.

State and persistence: state is stored in RustFS IAM users, canned policies, bucket policy documents, STS session credentials, object tags, and object data. Cleanup removes objects, buckets, users, and canned policies best-effort, but failure before cleanup can leave temporary server-side IAM state in the test environment.

Dependencies and integration points: depends on `crate::common` server/admin helpers, `aws_sdk_s3`, `awscurl`, STS SigV4 form POST support, `serial_test`, `uuid`, and RustFS IAM/policy/tagging internals. The tests exercise the S3 data plane, admin control plane, and STS endpoint together.

Risks: XML parsing is string-based and assumes un-namespaced STS response tags. `denied.is_err()` does not validate exact error code except in the multi-delete path. Tests are serial because they mutate global IAM-like state, and they require external `awscurl`. Cleanup is not guarded by a `Drop` helper, so early assertions can skip teardown.

Test signals: passing tests prove existing object tag conditions are re-evaluated for IAM, bucket, and STS session policies; bucket policies can grant tag-gated reads to a user without identity policy; STS inline policies restrict credentials; and multi-object delete reports mixed per-key success/failure without deleting denied keys.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/existing_object_tag_policy_test.rs -->
