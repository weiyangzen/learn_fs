# sources/object-store/rustfs/crates/protocols/src/common/gateway.rs

Purpose: This module is the authorization and capability gateway shared by protocol drivers. It translates protocol-visible S3 operations into RustFS IAM policy actions, checks whether an operation is supported for a protocol, and runs IAM authorization for a `SessionContext`.

Important APIs and types: `AuthorizationError` separates permanent `AccessDenied` from transient `IamUnavailable`. `S3Action` enumerates bucket, object, multipart, ACL, and copy operations exposed by gateways. `From<S3Action> for PolicyS3Action` and `From<S3Action> for rustfs_policy::policy::action::Action` bridge to the policy engine. `S3Action::as_str`, `is_operation_supported`, `is_authorized`, and `authorize_operation` are the main callable APIs. Under `cfg(test)`, `with_test_auth_override` and `with_test_iam_unavailable` provide per-thread authorization fixtures.

Control flow: `authorize_operation` first consults the test-only override when compiled for tests, then rejects unsupported protocol/action pairs, then calls `is_authorized`. `is_authorized` fetches the global IAM system, builds policy args from the session principal, groups, owner status, bucket, object, and claims, then awaits `iam_sys.is_allowed`. IAM acquisition failures are logged and returned as `IamUnavailable`; policy denies become `AccessDenied`.

State and persistence behavior: Production code has no local persistent state. It reads global IAM and global owner credentials. Test overrides are thread-local `RefCell`/`Cell` state with drop guards that clear decisions after an async body, preventing leaked permissions across tests.

Dependencies and integration points: It integrates `rustfs_iam`, `rustfs_policy`, `rustfs_credentials`, `serde_json`, and `SessionContext`. FTPS and SFTP drivers call `authorize_operation` before storage operations. The protocol support table is important: FTPS permits basic bucket/object listing and transfer but not multipart/copy/ACL; SFTP permits bucket/object operations plus multipart write and copy-object for rename; Swift and WebDAV are represented for cross-protocol capability checks.

Risks: The support matrix is security-sensitive; adding a new action or protocol without updating the exhaustive matches can cause build failures or unintended denial. `HeadObject` maps to `GetObject`, and multipart create/upload/complete map to `PutObject`, which is deliberate but must stay aligned with IAM policy expectations. Test override code must remain behind `cfg(test)` so production cannot bypass IAM.

Test signals: Tests verify allow/deny overrides, cleanup after the override body, closure visibility of action/bucket/object, fallback to IAM-unavailable when no override is installed, and precedence of the IAM-unavailable injection over allow overrides.
