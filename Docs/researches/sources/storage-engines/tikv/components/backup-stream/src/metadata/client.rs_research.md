# sources/storage-engines/tikv/components/backup-stream/src/metadata/client.rs

## Purpose
`metadata/client.rs` is the high-level API over backup stream metadata. It serializes task, range, pause, checkpoint, storage checkpoint, and last-error data into the `MetaStore` key space and translates watch events into `MetadataEvent`s consumed by the endpoint.

## Important APIs, types, and functions
- `MetadataClient<Store>` wraps a generic `MetaStore`, current store id, and per-task `CheckpointCache`s.
- `StreamTask` combines `StreamBackupTaskInfo` with a computed `is_paused` flag.
- `MetadataEvent` represents task add/remove, task pause/resume, and watch errors.
- `CheckpointProvider` and `Checkpoint` model checkpoint sources from store, region, task start, or central global checkpoint.
- Pause support uses `PauseV2`, `Payload`, `RFC3336Time`, and `PauseStatus` to store V1 empty pause markers or V2 JSON containing protobuf-encoded backup errors.
- Main methods include `init_task`, task getters/watchers, pause/resume APIs, last-error APIs, storage/local checkpoint setters/getters, range reads, checkpoint aggregation, task insertion/removal test helpers, and `get_region_checkpoint`.

## Control flow
Task loading reads task protobufs under the task prefix and checks the pause key for each task. `events_from` and `events_from_pause` create store watches from `revision + 1`, filter raw key-value events into typed metadata events, and increment metadata event metrics. Pause with error serializes a V2 JSON payload and writes it before returning; fatal endpoint handling separately records last error.

Checkpoint reads parse all keys under the task checkpoint prefix. `global_checkpoint_of` returns a central task/global checkpoint immediately if present, otherwise selects the smallest store checkpoint and ignores region checkpoints. `get_region_checkpoint` first checks the short-lived global cache, then reads the region checkpoint key, then falls back to global checkpoint or task start ts.

## State and persistence behavior
Durable metadata is written through `MetaStore`: task info protobufs, range start-to-end mappings, pause keys, last-error protobufs, local store checkpoints, storage checkpoints, and checkpoint keys. Checkpoint values are big-endian `u64` timestamps. In-memory cache state is held in a `DashMap<String, CheckpointCache>` and is not authoritative.

## Dependencies and integration points
The client depends on protobuf `StreamBackupTaskInfo` and `StreamBackupError`, metadata `keys`, `MetaStore`, TiKV metrics, `chrono` for pause time, base64/serde JSON for PauseV2, and `txn_types::TimeStamp`. `Endpoint` uses it for metadata watch, task registration, pause/fatal error handling, range loading, and checkpoint persistence.

## Risks and edge cases
- `get_last_error` reads a prefix and returns the first key-value without explicit ordering semantics beyond store behavior.
- `pause_with_err` falls back to an empty value if JSON serialization fails, preserving pause semantics but losing rich error details.
- `parse_ts_from_bytes` requires exactly 8 bytes; malformed values fail hard.
- `init_task` relies on conditional transaction support, which the PD store adapter does not implement through the generic `txn_cond` method.
- The method name `next_bakcup_ts_of_region` is misspelled but forms part of the internal API.

## Test signals
Local tests validate checkpoint key parsing for store and region providers. `metadata/test.rs` validates task/range insertion, watch event conversion, progress aggregation, storage checkpoint keys, storage checkpoint round trip, and idempotent task initialization.
