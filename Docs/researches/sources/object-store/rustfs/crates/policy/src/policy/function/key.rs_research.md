<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/key.rs

Purpose: Represents a condition key, including the known key name and optional variable suffix after a slash.

Important APIs/types/functions: `Key { name: KeyName, variable: Option<String> }` implements serde as/from a string. `Key::is`, `var_name`, and `name` expose comparisons and rendered names. `From<Key> for String` emits the full key string. `TryFrom<&str>` parses `name[/variable]`.

Control flow: Parsing splits the input at the first `/`; the prefix is parsed as `KeyName`, and any remainder is stored as `variable` without further validation. `name()` returns the short key name without the namespace prefix and appends `/variable` if present; `var_name()` returns the `${namespace:key}` variable placeholder from `KeyName`.

State/persistence behavior: No external state. This defines how condition keys are persisted in policy JSON and how they map to request context keys for evaluation.

Dependencies/integration: Uses `KeyName`, crate `Error`, policy `Error::InvalidKey`, and `Validator`. All typed condition functions depend on `Key`.

Risks/test signals: Variables are not validated for emptiness or allowed characters. `name()` strips the namespace prefix, so request context maps must use short names like `x-amz-copy-source` or `SourceIp` rather than full `s3:`/`aws:` keys. Tests cover serialization/deserialization success and invalid key names across namespaces.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/key.rs -->
