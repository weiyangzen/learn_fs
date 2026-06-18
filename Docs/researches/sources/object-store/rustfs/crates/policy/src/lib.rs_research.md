<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/lib.rs -->
# sources/object-store/rustfs/crates/policy/src/lib.rs

Purpose: Crate root for `rustfs-policy`; exposes the policy, auth, ARN, error, format, datetime, service type, and utility modules.

Important APIs/types/functions: Public modules are `arn`, `auth`, `error`, `format`, `policy`, `serde_datetime`, `service_type`, and `utils`. No functions or types are declared directly in this file.

Control flow: Rust module declaration only; it defines the public API surface and compilation units.

State/persistence behavior: None directly. It exposes modules that define persisted IAM/policy JSON shapes and serialization helpers.

Dependencies/integration: Used by downstream crates through module paths such as `rustfs_policy::policy::Policy`, `rustfs_policy::auth::UserIdentity`, and `rustfs_policy::error::Error`.

Risks/test signals: Publicly exposing `utils` may make helper internals part of the effective API. There are no root-level tests; correctness is compilation plus module-specific tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/lib.rs -->
