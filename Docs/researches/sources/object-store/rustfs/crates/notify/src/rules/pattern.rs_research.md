# sources/object-store/rustfs/crates/notify/src/rules/pattern.rs

## Purpose
Builds and evaluates wildcard object-key patterns from S3 notification prefix/suffix filters.

## Important APIs, types, and functions
- `new_pattern(prefix, suffix)` appends `*` after a non-empty prefix when needed, prepends `*` before a non-empty suffix when needed, concatenates both, and collapses `**` to `*`.
- `match_simple(pattern_str, object_name)` matches using `wildmatch::WildMatch`, with explicit match-all handling for `"*"` and empty-pattern no-match behavior.

## Control flow
Pattern construction handles prefix, suffix, both, or neither. Matching short-circuits `"*"` to true and `""` to false, then delegates wildcard matching.

## State and persistence behavior
Stateless helper module. Patterns are stored later in `PatternRules`.

## Dependencies and integration points
Used by XML filter conversion, global rule helpers, `PatternRules`, and tests. Depends on the `wildmatch` crate.

## Risks and edge cases
`*` matches across slashes, which is relied on by tests for nested paths. Empty prefix/suffix combinations can produce an empty pattern, but `RulesMap::add_rule_config` normalizes empty patterns to `"*"`. Direct callers of `match_simple("", key)` get false.

## Test signals
Tests cover prefix/suffix combinations, duplicate-star collapse, match-all behavior, empty patterns, nested slash matching, and complex wildcard forms.
