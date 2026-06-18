# sources/object-store/rustfs/crates/notify/src/rules/pattern_test.rs

## Purpose
Focused bug-reproduction and edge-case tests for prefix/suffix pattern construction and wildcard matching.

## Important APIs, types, and functions
- Tests `pattern::new_pattern` and `pattern::match_simple`.
- Covers prefix-only, suffix-only, prefix+suffix, empty pattern, complex paths, multiple slashes, and wildcard behavior.

## Control flow
Each test builds a pattern from prefix/suffix inputs or uses a literal pattern, then asserts matching and non-matching object keys.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Validates the primitive pattern helper used by XML filter parsing, global rule helpers, `PatternRules`, and `RulesMap`.

## Risks and edge cases
The tests intentionally confirm `*` spans slashes, so nested object keys match prefix/suffix rules. Empty pattern remains no-match at this helper layer, which differs from the match-all normalization in `RulesMap`.

## Test signals
Expected signals are exact generated pattern strings such as `uploads/*.csv`, positive nested matches, negative wrong-prefix/wrong-suffix matches, and match-all behavior for `"*"`.
