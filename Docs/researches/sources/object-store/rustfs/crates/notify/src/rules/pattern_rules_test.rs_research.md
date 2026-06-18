# sources/object-store/rustfs/crates/notify/src/rules/pattern_rules_test.rs

## Purpose
Comprehensive tests for `PatternRules` and `RulesMap` matching, set operations, event expansion, and target containment.

## Important APIs, types, and functions
- Pattern tests call `PatternRules::add`, `match_simple`, `match_targets`, `union`, `difference`, and `remove_pattern`.
- Rules map tests call `RulesMap::add_rule_config`, `has_subscriber`, `match_rules`, `remove_map`, and `contains_target_id`.
- Uses `EventName` compound and concrete variants plus `TargetID`.

## Control flow
The tests construct small rule maps by hand and assert matching outcomes for keys/events. Compound event tests add `ObjectCreatedAll` and then match concrete create events. Removal tests compare maps with same or different target IDs to verify difference semantics.

## State and persistence behavior
No persisted state; all maps and target IDs are local to tests.

## Dependencies and integration points
Validates the lower-level rules data structures used by `BucketNotificationConfig` and `NotifyRuleEngine`.

## Risks and edge cases
The tests encode the expectation that wildcard `*` matches nested paths and that empty filter strings become match-all only when passed through `RulesMap::add_rule_config`. They do not exercise the rayon branch because rule counts are small.

## Test signals
Signals include exact target membership, empty/non-empty target sets, event-specific routing, object-created compound expansion, and correct removal when the same target/pattern exists in another map.
