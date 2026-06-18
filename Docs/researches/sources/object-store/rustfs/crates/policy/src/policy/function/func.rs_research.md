<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/func.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/func.rs

Purpose: Provides the generic map representation shared by typed condition functions: policy condition keys mapped to operator-specific values.

Important APIs/types/functions: `InnerFunc<T>(Vec<FuncKeyValue<T>>)` stores one condition operator body. `FuncKeyValue<T>` stores `Key` and typed `values`. `InnerFunc::key_names` returns request-context short key names, and `contains_key_name` checks references. Custom serde serializes as a map from key to value and deserializes maps into `FuncKeyValue` entries.

Control flow: Deserialization visits a map, deserializes each key through `Key` and each value as `T`, pushes entries in input order, and rejects an empty map with `"has no condition key"`. Serialization emits each key/value pair.

State/persistence behavior: This is a persisted policy JSON shape but has no external state. It preserves input order in the internal vector, although equality for wrappers may treat vectors/order according to derived or custom comparisons.

Dependencies/integration: Used by string, address, binary, bool/null, date, and number condition modules. Depends on serde and `Key`/`KeyName`.

Risks/test signals: Duplicate keys in a condition map are not explicitly rejected here; serde map behavior and JSON parser behavior determine what reaches the visitor. Empty condition bodies are rejected at this lower level even though empty `Functions` is accepted. There are no direct tests in this file; typed function tests cover its serde path.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/func.rs -->
