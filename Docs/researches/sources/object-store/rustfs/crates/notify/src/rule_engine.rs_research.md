# sources/object-store/rustfs/crates/notify/src/rule_engine.rs

## Purpose
Stores per-bucket notification rules and resolves event/object pairs into target IDs for dispatch.

## Important APIs, types, and functions
- `NotifyRuleEngine` wraps `Arc<AsyncShardedHashMap<String, RulesMap, FxBuildHasher>>` with cached snapshots.
- `set_bucket_rules`, `get_bucket_rules`, and `clear_bucket_rules` mutate/query bucket rules.
- `has_subscriber` checks whether a bucket has rules for an event.
- `match_targets` returns all target IDs matching a bucket, event, and object key.
- `is_target_bound_to_any_bucket` scans all bucket rules for a target ID.
- `decoded_object_key_for_matching` percent-decodes encoded keys only when decoding changes the key.

## Control flow
Bucket config loading calls `set_bucket_rules`, which removes empty maps or inserts non-empty maps. Dispatch calls `match_targets`; this first matches the supplied object key and then, if the key contains percent escapes that decode successfully to a different string, also matches the decoded key and unions the results.

## State and persistence behavior
Bucket rules are in-memory in a sharded async map. There is no direct persistence here; bucket notification configuration loading supplies the maps.

## Dependencies and integration points
Uses `RulesMap`, `TargetIdSet`, `EventName`, `TargetID`, `starshard::AsyncShardedHashMap`, `percent_encoding`, and structured tracing. Called by `EventNotifier`, `NotifyConfigManager`, and bucket config APIs.

## Risks and edge cases
The target-bound scan iterates all bucket maps, which may be expensive with many buckets but is used for config deletion safety rather than per-event dispatch. Matching both raw and decoded keys is necessary because events encode keys while rules are often raw; malformed percent encodings simply skip the decoded pass.

## Test signals
Tests cover bucket rule lifecycle, subscriber checks, target-bound checks, matching results, and clearing behavior. Additional notifier tests cover encoded/decoded key matching and suffix-filter non-bypass.
