<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/effect.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/effect.rs

Purpose: Represents statement effects (`Allow` or `Deny`) and provides simple logic for translating a condition/resource/action match into an allowed result.

Important APIs/types/functions: `Effect` is a serde/strum enum with default `Allow`. `TryFrom<String>` parses effect strings. `Effect::is_allowed(allowed)` returns `allowed` for `Allow` and `!allowed` for `Deny`. It implements `Validator` with a no-op `is_valid`.

Control flow: Deserialization uses `try_from = "String"` and string enum parsing. `is_allowed` applies the effect as a boolean inversion for deny.

State/persistence behavior: Persisted as `"Allow"` or `"Deny"` in policy JSON. No in-memory state beyond enum value.

Dependencies/integration: Uses serde, `strum`, crate `Error`/`Result`, and policy `Validator`. Statement evaluation likely combines this with match results.

Risks/test signals: Defaulting to `Allow` can be dangerous if a missing/invalid effect path ever falls through to default construction rather than serde validation. `TryFrom` maps `strum::ParseError` to `Error::StringError`, not the inner `policy::Error::InvalidEffect`. No direct tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/effect.rs -->
