<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/bool_null.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/bool_null.rs

Purpose: Implements boolean condition operands for `Bool` and `Null` IAM condition operators.

Important APIs/types/functions: `BoolFunc` is `InnerFunc<BoolFuncValue>`. `evaluate_bool` compares configured booleans with request string values. `evaluate_null` checks request-key presence/absence. `BoolFuncValue` serializes booleans as strings and deserializes from bools, `"true"`/`"false"` strings, or a one-element array.

Control flow: `evaluate_bool` requires every configured key to have a first request value equal to the configured boolean's lowercase string; missing keys or mismatches fail. `evaluate_null` computes request vector length and, for a configured `true`, requires zero values; for `false`, requires at least one value. Deserialization rejects empty arrays, arrays with more than one value, and non-boolean strings.

State/persistence behavior: Policy JSON emits `"true"` or `"false"` strings even if input used JSON booleans. No external state.

Dependencies/integration: Uses serde visitors and `InnerFunc`. `Condition::Bool` and `Condition::Null` delegate here.

Risks/test signals: `evaluate_bool` only inspects the first request value, ignoring later values. A present key with an empty vector is considered null for `Null`. Tests cover bool/string/one-element-array deserialization, invalid inputs, variable suffix keys, and serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/bool_null.rs -->
