# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/request_info.rs

Purpose: small assertion helper validating request metadata attached to filesystem operations in tests.

Important APIs/types/functions: `assert_request_info_is_correct(req: &RequestInfo)` compares `req.uid` to `users::get_current_uid()` and `req.gid` to `users::get_effective_gid()`.

Control flow: direct assertions only. PID validation is present as a TODO and commented out because it did not work reliably.

State/persistence: reads process/user identity via the `users` crate; no storage or mutation.

Dependencies/integration: uses rustfs common `Uid`, `Gid`, and `RequestInfo`. Intended for mock expectation callbacks validating FUSE request context.

Risks: effective gid vs current uid assumptions can be environment-sensitive under sudo, containers, or test runners with changed credentials. PID remains unverified.

Test signals: assertion failures in tests indicate request context propagation regressions.
