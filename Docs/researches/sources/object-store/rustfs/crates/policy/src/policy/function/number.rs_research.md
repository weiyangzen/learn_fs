<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/number.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/number.rs

Purpose: Implements integer condition values and comparisons for numeric IAM operators.

Important APIs/types/functions: `NumberFunc` is `InnerFunc<NumberFuncValue>`. `NumberFunc::evaluate(op, if_exists, values)` applies a supplied integer comparison to request and policy values. `NumberFuncValue(i64)` serializes as a string and deserializes from JSON signed integers, unsigned integers, or numeric strings.

Control flow: For each configured key, evaluation reads the first request value. If missing, it returns the supplied `if_exists` boolean. If present, it parses the request as `i64` and applies `op(&request_value, &policy_value)`. Any parse failure or failed comparison returns false; all configured key comparisons must pass.

State/persistence behavior: Policy JSON emits numeric values as strings. No external state.

Dependencies/integration: Uses serde, `HashMap`, and `InnerFunc`. `Condition` passes the correct comparison functions and the `if_exists` flag for numeric variants.

Risks/test signals: `visit_u64` casts to `i64` with `as`, so values above `i64::MAX` wrap to negative numbers rather than being rejected. Only the first request value is considered. The dedicated `NumericGreaterThanIfExists` caller currently passes `i64::ge`, which changes strict greater-than semantics. Tests cover serde for integer and string inputs plus variable suffix keys; they do not cover overflow or evaluation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/number.rs -->
