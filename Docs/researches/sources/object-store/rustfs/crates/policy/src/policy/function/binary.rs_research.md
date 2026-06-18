<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/binary.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/binary.rs

Purpose: Implements AWS IAM `BinaryEquals` policy values and evaluation using base64-decoded byte comparison.

Important APIs/types/functions: `BinaryFunc` is `InnerFunc<BinaryFuncValue>`. `BinaryFuncValue` stores original encoded strings for serialization and decoded byte vectors for comparison. `BinaryFuncValue::new`, `TryFrom<String>`, `TryFrom<&str>`, custom serde, and `BinaryFunc::evaluate` provide parsing and evaluation. `BinaryFuncValueError::InvalidBase64` reports malformed values.

Control flow: Policy deserialization accepts one base64 string or a non-empty array, eagerly decodes every value, and rejects malformed base64 at parse time. Evaluation requires every configured key/value pair to match. For each key, missing request values return false; each request value is decoded from base64, and any malformed request value fails closed immediately; at least one decoded request value must equal one configured decoded value.

State/persistence behavior: No external state. Policy JSON round-trips the original encoded string/array form, while equality compares decoded bytes to avoid formatting differences.

Dependencies/integration: Uses `base64-simd`, serde, `HashMap`, and `InnerFunc`. `Condition::BinaryEquals` delegates directly here.

Risks/test signals: Failing closed on any invalid request value means a request with one valid matching binary value and one malformed value is denied. Empty arrays are rejected. Evaluation expects request context values to still be base64 strings, not raw decoded header bytes. Tests are strong: decoded match/non-match, missing/empty keys, multi-value OR behavior, invalid request fail-closed behavior, all-key AND behavior, serde parse rejection, and round-trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/binary.rs -->
