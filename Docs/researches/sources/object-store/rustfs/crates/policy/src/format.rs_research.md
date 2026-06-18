<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/format.rs -->
# sources/object-store/rustfs/crates/policy/src/format.rs

Purpose: Defines a minimal serializable IAM format/version marker.

Important APIs/types/functions: `Format` is a `Deserialize`, `Serialize`, `Default` struct containing `version: i32`. Commented code suggests intended constants for config path and default version.

Control flow: There is no behavior beyond serde/default construction.

State/persistence behavior: Intended as a persisted shape for IAM format metadata, likely under a config path, but current code only defines the struct and does not provide path/default helpers.

Dependencies/integration: Depends only on serde. Exposed publicly through `lib.rs`.

Risks/test signals: Default version is `0` because no custom `Default` impl exists, while comments suggest a default version of `1`; callers relying on `Default` may persist an unintended version. No tests cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/format.rs -->
