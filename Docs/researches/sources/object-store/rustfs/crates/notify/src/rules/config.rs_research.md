# sources/object-store/rustfs/crates/notify/src/rules/config.rs

## Purpose
Defines `BucketNotificationConfig`, the validated in-memory bucket notification configuration, and compiles it into both precise dispatch rules and fast subscriber snapshots.

## Important APIs, types, and functions
- `BucketNotificationConfig { region, rules: RulesMap }`.
- `new`, `add_rule`, `get_rules_map`, and `set_region` provide construction and mutation.
- `from_xml` parses `NotificationConfiguration`, applies defaults, validates region/ARNs, and converts queue configs into `RulesMap` entries.
- `validate` checks region equality and target ARN membership.
- `compile_snapshot` adapts `RulesMap` into `BucketRulesSnapshot<DynRulesContainer>`.
- Internal `RuleView` and `CompiledRules` adapt event keys into the `RulesContainer` trait used by subscriber snapshots.

## Control flow
XML parsing uses `NotificationConfiguration::from_reader`, `set_defaults`, and `validate`. Each queue config contributes its target ID, event list, and filter-derived pattern to `RulesMap::add_rule_config`. Snapshot compilation creates one `RuleView` per event key in the map and ORs event masks to produce the bucket snapshot mask.

## State and persistence behavior
This type is in-memory and serializable/deserializable. It does not persist itself; callers load it into `NotifyRuleEngine` and `NotificationSystemSubscriberView`.

## Dependencies and integration points
Uses `RulesMap`, `xml_config`, `subscriber_snapshot`, `EventName`, `TargetID`, and serde. It is consumed by global rule helpers, bucket config manager, and notification system facade methods.

## Risks and edge cases
`CompiledRules` currently tracks event presence only for subscriber checks, not full pattern/target details. `validate` reconstructs ARNs from target IDs and region, so ARN formatting must match `TargetID::to_arn`. Empty patterns are converted to match-all by `RulesMap`.

## Test signals
Integration tests in `config_test.rs` exercise XML parsing, prefix/suffix filters, no-filter match-all, multiple queues, region defaults, ARN validation, capitalized filter names, and compound event expansion.
