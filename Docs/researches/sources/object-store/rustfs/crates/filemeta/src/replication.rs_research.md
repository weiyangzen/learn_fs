# sources/object-store/rustfs/crates/filemeta/src/replication.rs

## Purpose

This module defines replication status, purge status, replication decisions, MRF replay entries, worker-operation abstraction, and helpers for converting per-target state into internal metadata strings and composite object status. It is the metadata-side model used by object replication, delete replication, heal replication, resync, and recovery queues.

## Important APIs, Types, and Functions

- Constants such as `REPLICATE_QUEUED`, `REPLICATE_EXISTING`, `REPLICATE_MRF`, `REPLICATE_INCOMING`, and heal/delete variants name replication audit/event origins.
- `ReplicationStatusType` models S3-style `PENDING`, `COMPLETED`, legacy `COMPLETE`, `FAILED`, `REPLICA`, and empty states, with string conversion and conversion from `VersionPurgeStatusType`.
- `VersionPurgeStatusType` models `PENDING`, `COMPLETE`, `FAILED`, and empty purge states.
- `ReplicationType` models object/delete/metadata/heal/existing/resync/all operation kinds and has validity/data-replication helpers.
- `ReplicationState` stores timestamps, replica status, internal replication/purge status strings, parsed target maps, reset status map, and replicate-decision string. It provides `equal`, composite status helpers, and `target_state`.
- `get_composite_replication_status()` and `get_composite_version_purge_status()` reduce target maps to overall status.
- `ReplicationAction`, `ReplicatedTargetInfo`, and `ReplicatedInfos` describe per-target results and aggregate completed size, resync occurrence, internal status strings, aggregate status, purge status, and action.
- `MrfOpKind` and `MrfReplicateEntry` define persisted Most Recent Failures queue entries, with serde defaults for backward compatibility.
- `ReplicationWorkerOperation` is a trait abstraction for queued replication work.
- `ReplicateTargetDecision` and `ReplicateDecision` model per-target replication decisions and can render pending status or parse string decisions with `parse_replicate_decision`.
- `ReplicateObjectInfo` is the concrete object/delete replication work item and implements `ReplicationWorkerOperation`.
- `replication_statuses_map()`, `version_purge_statuses_map()`, `get_replication_state()`, and `target_reset_header()` convert between strings, maps, and persisted state.
- `ResyncDecision` and `ResyncTargetDecision` model target-specific resync requirements.

## Control Flow

Status conversion is mostly enum/string mapping. Composite status reduction returns failed if any target failed, completed/complete only if all targets completed, pending otherwise, and empty when there are no targets.

`ReplicationState::composite_replication_status()` first honors a simple internal status string if it is one of the known direct statuses. Otherwise it reduces parsed target statuses. If a replica timestamp is newer than the replication timestamp and all targets look completed, it can return the replica status instead. Purge status follows the same direct-string-first, map-reduction-second pattern.

`ReplicatedInfos` builds internal status strings in `arn=status;` form, skipping empty targets and empty purge statuses. `action()` returns the replication action from the first target that was not already completed.

`parse_replicate_decision()` parses comma-delimited `key=replicate;synchronous;arn;id` items. It rejects malformed pairs or target strings with `InvalidInput`.

`ReplicateObjectInfo::target_replication_status()` applies a lazily compiled regex to `replication_status_internal` and returns the matching ARN status. `to_mrf_entry()` serializes core replay fields; both the trait implementation and inherent method currently set `op` to `MrfOpKind::Object`.

`get_replication_state()` merges new `ReplicatedInfos` into previous state by preserving previous replica fields and decision string, adding reset timestamps, rebuilding parsed target maps from generated internal strings, and setting replication/purge timestamps/status strings.

## State and Persistence Behavior

Replication state is persisted mainly as strings in internal metadata. Target statuses use `arn=status;` format parsed by a global regex. Reset status keys are persisted with `internal_key_rustfs("replication-reset-{arn}")`. `MrfReplicateEntry` is serde-serializable and intentionally backward-compatible: missing `versionID`, `op`, `deleteMarkerVersionID`, `deleteMarker`, and `size` fields default safely for old queue entries.

Timestamps are `OffsetDateTime`; durations are stored in `ReplicatedTargetInfo` for runtime result reporting. Decision and resync maps are normal Rust maps and are rendered only where needed.

## Dependencies and Integration Points

The module uses `bytes::Bytes`, `regex::Regex`, `LazyLock`, `serde`, `time`, `uuid`, `Duration`, and `rustfs_utils::http::internal_key_rustfs`. It integrates with `version.rs` through `get_internal_replication_state()`, which parses internal metadata into `ReplicationState`, and with replication workers/managers through `ReplicationWorkerOperation`, `ReplicateObjectInfo`, and MRF entries.

## Risks and Edge Cases

- `REPL_STATUS_REGEX` is `([^=].*?)=([^,].*?);`; it is permissive and can match broad substrings. ARNs or malformed status strings containing delimiters may parse unexpectedly.
- `parse_replicate_decision()` splits on every `=` and requires exactly two parts, so ARNs/ids containing `=` would break parsing.
- `ReplicateObjectInfo::to_mrf_entry()` always writes `MrfOpKind::Object`, even when `op_type` or `delete_marker` indicates delete work. Delete-specific MRF fields are therefore not populated by this method.
- `ReplicationStatusType::CompletedLegacy` exists but composite map reduction counts only `Completed` as complete. Legacy `COMPLETE` parsed from per-target maps will not count as completed.
- `ReplicationState::equal()` compares only status fields, not timestamps, target maps, purge maps, reset maps, or decisions. This is intentional if equality means "status-equivalent", but risky if used as full-state equality.
- Display/string serialization iterates hash maps, so output ordering is nondeterministic.

## Test Signals

This file has no local test module. It is indirectly exercised by `version.rs` object/delete conversion tests that parse internal replication/purge metadata and by higher-level replication/heal code that consumes these exported types.
