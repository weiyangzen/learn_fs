# sources/object-store/rustfs/crates/policy/src/policy/function/string.rs

## Purpose

Implements IAM string condition functions for policy evaluation. This file backs operators such as string equality, string inequality through negation, case-insensitive equality, wildcard-like matching, and ForAllValues/ForAny-style behavior over request context values. It also defines the JSON value shape used by string functions.

## Important APIs, Types, and Functions

- `pub type StringFunc = InnerFunc<StringFuncValue>` is the concrete string condition function container.
- `StringFunc::evaluate_with_resolver(...)` evaluates all contained key/value clauses and combines them with logical AND. Flags select all-values semantics, case folding, wildcard matching, and negation.
- `FuncKeyValue<StringFuncValue>::eval(...)` performs exact string set matching. It resolves policy variables, substitutes common condition variables, optionally lowercases request and policy values, and compares request values against function values.
- `FuncKeyValue<StringFuncValue>::eval_like(...)` performs wildcard pattern matching using `policy::utils::wildcard::is_match`.
- `StringFuncValue(pub Set<String>)` stores non-empty condition values. Tests use `BTreeSet` for deterministic serialization, while production uses `HashSet`.
- Custom `Serialize` accepts/outputs a single string when there is exactly one value and a sequence for multiple values. Custom `Deserialize` accepts either a string or array and rejects empty arrays.

## Control Flow

Evaluation iterates over each `FuncKeyValue`. For non-like conditions, request values are read from `values` by `self.key.name()`, normalized for case if needed, and collected into a set. Policy-side values are asynchronously expanded through `resolve_aws_variables` when a resolver is present. Each expanded value also receives direct substitution for `KeyName::COMMON_KEYS` by replacing `${...}` variable forms with the first non-empty request condition value. The final result is an intersection check: `for_all` accepts empty request sets or requires all request values to be in the policy set; non-`for_all` requires at least one intersection.

For like conditions, each request value is tested against every resolved/substituted policy pattern using wildcard matching. With `for_all`, every request value must match at least one pattern; without it, any match succeeds. If the key is missing, `eval_like` returns `for_all`, matching the vacuous truth behavior also visible in tests.

`evaluate_with_resolver` XORs each clause result with `negate` and returns false on the first failed clause, so all clauses must pass after operator-specific negation.

## State and Persistence

This file is stateless. It allocates temporary sets/vectors during each evaluation and awaits policy-variable resolution. No persistent storage, global mutable state, or I/O is used.

## Dependencies and Integration Points

Depends on `FuncKeyValue`, `InnerFunc`, `KeyName`, `PolicyVariableResolver`, and `resolve_aws_variables` from the policy function/variable subsystem. It integrates with the broader `Functions` condition evaluator, with request condition maps supplied by statement and policy evaluation. Wildcard matching is delegated to `policy::utils::wildcard`.

## Risks and Edge Cases

- `for_all` returns true for missing request values, which is intentional in tests but sensitive for authorization semantics.
- Policy variable expansion can produce multiple candidate values; callers must understand this can widen matches.
- Common key substitution uses only the first non-empty request value, so multi-valued request keys do not generate combinations through this compatibility path.
- Production `HashSet` serialization order is not deterministic unless higher layers preserve or sort elsewhere; tests switch to `BTreeSet`.
- Lowercasing uses `to_lowercase`, which can expand Unicode characters; comparisons are string-based rather than locale-aware.

## Test Signals

Inline tests cover JSON deserialization/serialization, invalid keys and empty values, JWT role key matching, exact equality and negation, case-insensitive variants, wildcard like/not-like, `for_all` behavior, missing-key behavior, `s3:LocationConstraint` substitution, and tag-key specific condition matching.
