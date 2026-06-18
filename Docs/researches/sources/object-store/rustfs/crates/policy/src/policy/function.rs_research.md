<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function.rs

Purpose: Aggregates policy condition operators into `Functions`, handling `ForAnyValue`, `ForAllValues`, and normal condition groups, plus serde and evaluation dispatch.

Important APIs/types/functions: `Functions` stores three vectors of `Condition`: `for_any_value`, `for_all_values`, and `for_normal`. `evaluate` and `evaluate_with_resolver` run all conditions asynchronously. `is_empty` and `references_key_name` support validation and policy analysis. Custom serde serializes/deserializes condition maps with optional `ForAnyValue:` or `ForAllValues:` qualifiers. `Value` is an unused serializable marker type.

Control flow: Evaluation short-circuits false. `ForAnyValue` conditions pass `for_all=false`, `ForAllValues` pass `for_all=true`, and normal conditions pass `for_all=false` into each `Condition`. Deserialization rejects duplicate operator keys, parses at most one qualifier prefix separated by `:`, rejects unknown qualifiers or extra separators, and delegates each operator body to `Condition::from_deserializer`.

State/persistence behavior: No external state. The persisted policy shape is a JSON map whose keys are condition operator names, optionally prefixed with `ForAnyValue:` or `ForAllValues:`. Empty maps are accepted; a commented block suggests they may once have been rejected.

Dependencies/integration: Re-exports and uses submodules `addr`, `binary`, `bool_null`, `condition`, `date`, `func`, `key`, `key_name`, `number`, and `string`. Async evaluation can use `PolicyVariableResolver` to resolve policy variables through string conditions.

Risks/test signals: Duplicate detection uses the raw operator key string, so semantically related keys like `StringEquals` and `StringEqualsIfExists` are distinct. Empty condition maps evaluate true. Evaluation order is deterministic by vector order from serde map traversal. Tests cover many deserialization shapes, numeric/date/string/ARN operator parsing, IfExists syntax, and serialization ordering for grouped conditions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function.rs -->
