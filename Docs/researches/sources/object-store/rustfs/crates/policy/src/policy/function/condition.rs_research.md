<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/condition.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/condition.rs

Purpose: Defines the condition-operator enum and dispatches parsing, serialization, key-reference analysis, and asynchronous evaluation for all policy condition types.

Important APIs/types/functions: `Condition` variants cover string/ARN equals/like/not/ignore-case operators, `BinaryEquals`, `IpAddress`, `NotIpAddress`, `Null`, `Bool`, numeric comparisons, date comparisons, dedicated `NumericGreaterThanIfExists`, and generic `IfExists(Box<Condition>)`. Key functions include `from_deserializer`, `to_key`, `to_key_with_suffix`, `has_any_key_in`, `references_key_name`, `evaluate_with_resolver`, `is_negate`, and `serialize_map`.

Control flow: `from_deserializer` maps an operator key to a typed condition body; unknown keys ending in `IfExists` recursively parse the base operator and wrap it. Evaluation delegates to typed functions: string/ARN operators use `StringFunc::evaluate_with_resolver` with flags for case, wildcard, and negation; binary/IP/bool/null/number/date use their specialized evaluators. Generic `IfExists` returns true when none of the referenced keys appear in the request context, otherwise delegates to the inner condition. After delegate evaluation, `is_negate` currently only inverts `NotIpAddress`; string negations are handled by flags to avoid double negation.

State/persistence behavior: No external state. Serde uses `to_key_with_suffix` and `serialize_map` so wrapper conditions serialize as operator keys like `StringEqualsIfExists`; nested wrappers serialize with repeated suffixes.

Dependencies/integration: Integrates all function operand modules, `PolicyVariableResolver`, `KeyName`, serde map APIs, `HashMap`, and `time::OffsetDateTime`. It is the central dispatch point used by `Functions`.

Risks/test signals: `NumericGreaterThanIfExists` delegates to `i64::ge` rather than `i64::gt`, so its semantics look like greater-than-or-equal if present. There is no generic `IfExists` special handling for all dedicated variants beyond suffix parsing; nested IfExists is allowed and serialized. `NotIpAddress` is the only post-dispatch negation; other future negative operators must avoid double-negation mistakes. Tests specifically cover StringNotEquals no double negation, absent-key behavior, IfExists serialization/deserialization, and IfExists evaluation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/condition.rs -->
