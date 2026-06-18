# sources/object-store/rustfs/crates/notify/src/rules/target_id_set.rs

## Purpose
Defines the target-ID set type used throughout notification rule matching.

## Important APIs, types, and functions
- `pub type TargetIdSet = HashSet<TargetID>`.
- `new_target_id_set` converts a vector of target IDs into a set; it is crate-private and currently allowed dead code.

## Control flow
No significant logic beyond vector-to-set collection.

## State and persistence behavior
No owned state; the type alias is used inside rule maps and pattern rules.

## Dependencies and integration points
Uses `hashbrown::HashSet` and `rustfs_targets::arn::TargetID`. Used by `PatternRules`, `RulesMap`, and `NotifyRuleEngine`.

## Risks and edge cases
Set ordering is nondeterministic, so tests that collect into vectors must account for order unless only one target is present. The helper is unused, indicating either planned Go-style API compatibility or leftover scaffolding.

## Test signals
Indirectly covered by rule matching tests that assert target membership and set lengths.
