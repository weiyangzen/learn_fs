<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/error.rs -->
# sources/object-store/rustfs/crates/policy/src/error.rs

Purpose: Defines the crate-wide `Error` and `Result` types for IAM/policy operations outside the inner policy syntax module, along with helper predicates for common not-found variants.

Important APIs/types/functions: `Error` variants cover wrapped `policy::Error`, string errors, crypto/JWT errors, IAM not-found cases, invalid arguments/state, credential/key problems, access denial, policy size, I/O, and initialization conflicts. `Error::other` wraps arbitrary errors as `std::io::Error::other`. `From` impls convert `std::io::Error`, `time::error::ComponentRange`, `serde_json::Error`, and `regex::Error`; `thiserror` derives conversions for policy, crypto, and JWT errors. Predicate helpers include `is_err_no_such_policy`, `is_err_no_such_user`, `is_err_no_such_account`, `is_err_no_such_temp_account`, `is_err_no_such_group`, and `is_err_no_such_service_account`.

Control flow: Callers use `?` to convert lower-level errors into this enum. Non-enum arbitrary errors are intentionally collapsed into `Error::Io(ErrorKind::Other)` through `Error::other`, preserving display text but losing precise type information.

State/persistence behavior: Stateless error representation. The display strings are user/API visible and may be part of compatibility expectations.

Dependencies/integration: Bridges `crate::policy`, `rustfs_crypto`, `jsonwebtoken`, `serde_json`, `time`, `regex`, and standard I/O. The auth, ARN, and policy modules return this `Result` for operational errors.

Risks/test signals: Converting JSON/time/regex failures into I/O `Other` obscures source categories. There is both `StringError` and `Error::other`, so callers may produce inconsistent variants for similar failures. Tests cover conversions, helper predicates, display formatting for many variants, and `StringError`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/error.rs -->
