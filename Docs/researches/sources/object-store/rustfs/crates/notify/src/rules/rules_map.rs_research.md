# sources/object-store/rustfs/crates/notify/src/rules/rules_map.rs

## Purpose
Organizes notification rules by `EventName`, expands compound event subscriptions, and provides fast event-mask checks plus precise object-key matching.

## Important APIs, types, and functions
- `RulesMap { map: HashMap<EventName, PatternRules>, total_events_mask: u64 }`.
- `add_rule_config` normalizes empty pattern to `"*"`, expands compound events via `EventName::expand`, inserts pattern/target rules, and updates the mask.
- `add_map`, `remove_map`, `remove_rule`, `remove_rules`, and `update_rule` support map mutations.
- `has_subscriber` uses the total mask.
- `match_rules` returns targets for a concrete event/key.
- `contains_target_id`, `inner`, `is_empty`, and `iter_events` expose inspection.

## Control flow
Rules are stored under concrete expanded event names. Matching first checks the event mask, then looks up the concrete event and delegates to `PatternRules::match_targets`. Removal recalculates the mask to avoid stale subscriber bits.

## State and persistence behavior
In-memory and serde-serializable. It is stored inside `BucketNotificationConfig` and in `NotifyRuleEngine` bucket maps.

## Dependencies and integration points
Uses `PatternRules`, `TargetIdSet`, `EventName`, `TargetID`, `hashbrown`, and serde. It is central to dispatch matching and subscriber snapshot compilation.

## Risks and edge cases
`has_subscriber(ObjectCreatedAll)` returns true if any object-created bit is present, which is useful as a broad mask check but not equivalent to all concrete events being configured. `match_rules` expects concrete event names after expansion; callers using compound events directly may get no precise pattern map entry.

## Test signals
Tests cover basic routing, compound expansion, prefix/suffix bug flow, multiple patterns, prefix-only, suffix-only, no-filter match-all, different event types, map removal, and target containment.
