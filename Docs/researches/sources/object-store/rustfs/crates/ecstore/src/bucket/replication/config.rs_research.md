# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/config.rs

Purpose: Adds replication decision logic to S3 `ReplicationConfiguration`. It filters rules, determines whether an object/delete/resync operation should replicate, and extracts target ARNs.

Important APIs and types: `ObjectOpts` describes an operation: object name, tags, version ID, delete marker status, SSE-C flag, replication type, replica/existing flags, and optional target ARN. `ReplicationConfigurationExt` provides `replicate`, `has_existing_object_replication`, `filter_actionable_rules`, `get_destination`, `has_active_rules`, and `filter_target_arns`.

Control flow and state: `filter_actionable_rules` skips disabled rules, target mismatches, invalid empty object names for normal operations, disabled existing-object rules, prefix mismatches, and tag-filter mismatches. Resync and All operations include rules early. Matched rules are sorted by priority when destinations match. `replicate` handles delete semantics separately: versioned delete markers require enabled delete-marker replication, versioned object deletes require enabled delete replication, and non-versioned deletes follow delete-marker replication. Non-delete operations use `rule.metadata_replicate`.

Dependencies and integration: Uses `rustfs_filemeta::ReplicationType`, S3 replication DTOs, `ReplicationRuleExt` from sibling rule module, and tag decoding from bucket tagging. Re-exported by `replication/mod.rs` for replication pool/resync paths.

Risks: Sorting only orders rules when destinations are equal; multi-destination ordering remains original/unspecified. `replicate` returns based on the first actionable rule, so later matching rules are ignored. Tag decode failures likely become empty maps depending on `decode_tags_to_map`, affecting filtered replication.

Test signals: Tests cover target ARN extraction with multiple destinations, role fallback, excluding disabled existing-object targets for existing-object operations, and including them for heal operations.
