<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/src/lib.rs -->
# sources/object-store/rustfs/crates/s3-ops/src/lib.rs

## Purpose
Defines `S3Operation` and maps S3 API operations to notification `EventName` values. It also provides helper functions for event compatibility, delete-marker event selection, POST-vs-PUT object-created events, and object-created mask construction.

## Important APIs, types, and functions
- `S3Operation` enumerates bucket, object, multipart, ACL, lifecycle, replication, restore, select, and public-access operations.
- `S3Operation::as_str` returns IAM-style names such as `s3:PutObject`.
- `to_event_name`, `event_name_to_s3_operation`, and `operation_matches_event_name` map between operations and events.
- `delete_event_name_for_marker`, `put_event_name_for_post_object`, `is_object_removed_event`, and `put_object_created_event_mask` encode common notification decisions.
- Private `EventMapping` handles one-to-many compatibility.

## Control flow
Each operation maps through `event_mapping`. Simple operations use `Single(EventName)`, while `PutObject`, `DeleteObject`, and `DeleteObjects` have custom matching sets. The reverse mapping matches event variants to the best corresponding S3 operation and returns `None` for compound or internal events with no public operation.

## State and persistence behavior
No state is stored. The mappings are pure constants in match expressions. Their outputs influence emitted notification records and filtering masks, which are persisted or delivered by higher-level notification systems.

## Dependencies and integration points
Depends on `rustfs_s3_types::EventName`. Higher-level S3 handlers can use this crate to convert executed operations into notification event names and to test whether configured event subscriptions match an operation.

## Risks and edge cases
Mappings are semantic contracts. Unmapped operations such as `UploadPart` intentionally emit no event here, while complete multipart upload does. Batch delete can match both internal batch and per-object delete events. Adding a new `EventName` or `S3Operation` requires updating both forward and reverse matches plus tests.

## Test signals
Tests cover operation-to-event mapping, event-to-operation mapping, multi-variant operation matching, delete-marker and POST-object helpers, object-removed detection, created-event mask bits, and unmapped operation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-ops/src/lib.rs -->
