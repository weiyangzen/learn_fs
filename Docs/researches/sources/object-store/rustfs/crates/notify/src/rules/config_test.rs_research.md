# sources/object-store/rustfs/crates/notify/src/rules/config_test.rs

## Purpose
Integration-style unit tests for XML bucket notification configuration, from S3 XML parsing through `BucketNotificationConfig` to `RulesMap` event/object matching.

## Important APIs, types, and functions
- Uses `BucketNotificationConfig::from_xml`, `RulesMap::has_subscriber`, and `RulesMap::match_rules`.
- Builds ARNs with `rustfs_targets::arn::{ARN, TargetID}` and XML strings with queue configurations.
- Covers direct `FilterRule` layout and `FilterRuleList` wrapper layout.

## Control flow
Each test creates XML, supplies current region and allowed ARN list, parses into config, inspects generated rules, and asserts event/key matching. Compound event tests verify `ObjectCreatedAll` expands to concrete create events. Multiple queue tests ensure distinct target IDs are preserved per pattern.

## State and persistence behavior
No persistent state. Tests use in-memory XML cursors and in-memory rule maps.

## Dependencies and integration points
Exercises `xml_config`, `BucketNotificationConfig`, `RulesMap`, `pattern`, `EventName::expand/mask`, and `TargetID` ARN conversion together.

## Risks and edge cases
The URL-encoded key test documents that direct `RulesMap` matching of encoded spaces may or may not match; production encoded-key compensation happens in `NotifyRuleEngine`, not directly in `RulesMap`. Several tests print debug information, which can add noise but helps diagnose pattern generation.

## Test signals
Signals include expected matches for `uploads/*.csv`, prefix-only, suffix-only, no-filter match-all, specific event-only matching, capitalized filter names, multiple queues/targets, and compound event expansion excluding tagging events.
