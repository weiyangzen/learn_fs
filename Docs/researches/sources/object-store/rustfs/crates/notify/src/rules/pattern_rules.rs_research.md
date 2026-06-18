# sources/object-store/rustfs/crates/notify/src/rules/pattern_rules.rs

## Purpose
Stores target subscriptions by object-key pattern for a single event and resolves object keys to target ID sets.

## Important APIs, types, and functions
- `PatternRules { rules: HashMap<String, TargetIdSet> }`.
- `add`, `match_simple`, `match_targets`, `is_empty`, `inner`, `contains_target_id`, and `remove_pattern`.
- Set operations: `union`, `difference`, `union_in_place`, `difference_in_place`.
- `match_targets` uses a serial path below `PAR_THRESHOLD` 128 and a rayon parallel fold/reduce path for large rule sets.

## Control flow
Rules are added by pattern and target ID. Matching iterates patterns, applies `pattern::match_simple`, and extends a result set with all matching targets. Difference operations remove matching target IDs per pattern and drop empty pattern entries.

## State and persistence behavior
In-memory, serde-serializable rule map. It is embedded in `RulesMap` and not persisted directly by this module.

## Dependencies and integration points
Uses `hashbrown`, `rayon`, `TargetID`, `TargetIdSet`, and `pattern`. Called by `RulesMap` for event-specific matching and merging/removal.

## Risks and edge cases
The parallel path only helps large rule maps and depends on `TargetID` hashing/clone costs. Wildcard matching semantics come from `wildmatch`; because `*` matches slashes, prefix filters include nested subpaths. Difference behavior removes target IDs, not entire patterns unless their set becomes empty.

## Test signals
Tests in `pattern_rules_test.rs` cover basic matching, multiple patterns/targets, prefix/suffix bug scenarios, match-all, empty rules, union/difference, removal, and target containment.
