# sources/object-store/rustfs/crates/notify/src/rules/mod.rs

## Purpose
Module hub for notification rule parsing, pattern matching, rule maps, subscriber snapshots, target ID sets, and XML configuration.

## Important APIs, types, and functions
- Declares private modules `config`, `pattern_rules`, `rules_map`, `subscriber_index`, `subscriber_snapshot`, and `target_id_set`.
- Public modules: `pattern` and `xml_config`.
- Test modules are included only under `cfg(test)`.
- Re-exports `BucketNotificationConfig`, `PatternRules`, `RulesMap`, subscriber index/snapshot types, `TargetIdSet`, `NotificationConfiguration`, and parse error aliases.

## Control flow
No runtime logic. It organizes module visibility and API exports.

## State and persistence behavior
No local state. Re-exported types manage in-memory rules and snapshots elsewhere.

## Dependencies and integration points
This is the import surface for `crate::rules::*` used by config manager, global helpers, notifier tests, rule engine, and bucket config manager.

## Risks and edge cases
Changing re-exports can break callers even when internal modules remain intact. `xml_config` is public while most rule internals are private, reflecting the expected external XML API.

## Test signals
Compilation of rule tests validates module wiring. No direct tests in this file.
