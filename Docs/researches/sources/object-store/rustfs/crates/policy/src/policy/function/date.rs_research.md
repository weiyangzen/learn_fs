<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/date.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/date.rs

Purpose: Implements RFC3339 date/time condition values and comparisons for date IAM operators.

Important APIs/types/functions: `DateFunc` is `InnerFunc<DateFuncValue>`. `DateFunc::evaluate(op, values)` compares configured `OffsetDateTime` values with request context values using the supplied comparison function. `DateFuncValue` wraps `OffsetDateTime` with custom RFC3339 serde.

Control flow: For every configured key/value pair, evaluation reads the first request value by short key name, parses it as RFC3339, and applies the comparison as `op(&policy_value, &request_value)`. Missing or unparsable request values fail. Serialization formats the policy value using `Rfc3339`.

State/persistence behavior: Policy JSON stores dates as RFC3339 strings. No external state.

Dependencies/integration: Uses `time::OffsetDateTime` and the well-known `Rfc3339` format, serde, `HashMap`, and `InnerFunc`. `Condition` supplies equality/ordering functions for date variants.

Risks/test signals: Comparison argument order is policy value first and request value second, which must be checked against intended IAM semantics for less-than/greater-than operators. Only the first request value is considered. Tests cover parsing and serialization for object-lock retain-until date keys with and without variable suffixes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/date.rs -->
