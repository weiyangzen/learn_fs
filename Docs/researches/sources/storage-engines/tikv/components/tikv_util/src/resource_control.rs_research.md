# sources/storage-engines/tikv/components/tikv_util/src/resource_control.rs

## Purpose
Encodes resource-control task metadata compactly and maps override priorities to TiKV task-priority classes.

## Important APIs, Types, and Functions
- `DEFAULT_RESOURCE_GROUP_NAME` is `"default"`.
- `TaskMetadata<'a>` wraps borrowed or owned bytes using `Cow`.
- `TaskMetadata::from_ctx` encodes non-default `ResourceControlContext` fields into a mask byte plus optional native-endian priority and group name bytes.
- `override_priority`, `group_name`, `to_vec`, and `deep_clone` decode or materialize metadata.
- `priority_from_task_meta` and `TaskPriority::{High,Medium,Low}` map resource priorities to scheduling classes.

## Control Flow
Encoding sets bit flags for nonzero override priority and non-default group name. Empty metadata means priority zero and group `"default"`. Decoding checks the mask, reads four bytes after the mask when priority exists, and computes the group-name offset from whether priority was present.

## State and Persistence Behavior
Metadata is byte-level in-memory state that can be owned or borrowed. It is not self-describing beyond the first-byte mask and is not versioned.

## Dependencies and Integration Points
Depends on `kvproto::kvrpcpb::ResourceControlContext` and `strum` enum helpers. It is likely carried with tasks/requests to scheduling and resource control queues.

## Risks
Priority is encoded with `to_ne_bytes`, so bytes are native-endian and should not be treated as portable wire data across architectures. Decoding assumes valid lengths and will panic on malformed metadata with a priority mask but fewer than five bytes. Debug assertion allows priorities up to 16 but release builds still map all larger values to `High`.

## Test Signals
Tests cover default and non-default group/priority encoding round-trips and priority mapping boundaries for low, medium, and high.
