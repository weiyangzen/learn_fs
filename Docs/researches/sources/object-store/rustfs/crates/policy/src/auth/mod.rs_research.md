<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/auth/mod.rs -->
# sources/object-store/rustfs/crates/policy/src/auth/mod.rs

Purpose: Public authentication module that re-exports credential helpers and defines persisted user identity metadata around `rustfs_credentials::Credentials`.

Important APIs/types/functions: `pub use credentials::*` exposes the credential API. `UserIdentity` stores `version`, `credentials`, and optional `update_at` timestamp serialized as `updatedAt` with `update_at` alias. `UserIdentity::new`, `From<Credentials>`, `add_ssh_public_key`, and `get_ssh_public_keys` manage identity creation and SFTP public-key claims.

Control flow: New identities set version `1` and `update_at` to `OffsetDateTime::now_utc()`. SSH key addition lazily creates `credentials.claims` and inserts `"ssh_public_keys"` as a JSON array containing the provided key. Retrieval walks optional claims, expects an array, filters string values, and returns an empty vector for missing/malformed data.

State/persistence behavior: `UserIdentity` is a serializable storage shape. Timestamp serde accepts legacy `update_at` but emits `updatedAt`; this preserves compatibility with MinIO/RustFS-style IAM JSON. SSH keys are persisted inside credential claims.

Dependencies/integration: Uses the private `credentials` module, `rustfs_credentials::Credentials`, serde, serde JSON, `HashMap`, `time::OffsetDateTime`, and crate datetime serde helpers. Identity values are likely stored by IAM user/account subsystems.

Risks/test signals: `add_ssh_public_key` replaces any existing `"ssh_public_keys"` claim instead of appending, so multiple calls keep only the last key. There is no validation of SSH public key syntax. Tests cover deserializing MinIO-style RFC3339 `updatedAt`; no tests cover SSH key mutation or legacy `update_at` alias.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/auth/mod.rs -->
