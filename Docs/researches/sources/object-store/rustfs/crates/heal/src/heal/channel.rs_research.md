<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/channel.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/channel.rs

## Purpose

`channel.rs` adapts the common RustFS heal channel protocol into local `HealManager` operations. It receives start, query, and cancel commands from `rustfs_common::heal_channel`, converts user/admin-facing request shapes into internal `HealRequest` values, submits them to the manager, and publishes both oneshot replies and broadcast `HealChannelResponse` messages. It is the boundary between admin/API command handling and the internal queue/scheduler/task model.

## Important APIs, types, and functions

- `HealChannelProcessor` owns an `Arc<HealManager>`, an unbounded response sender, and an unbounded local response receiver used to observe locally published responses.
- `HealTaskStatusPayload` is the JSON payload for query responses, carrying a MinIO-style `summary` string plus `HealResultItem` details.
- `new` creates the processor and local response channel.
- `start` runs a `tokio::select!` loop over inbound `HealChannelReceiver` commands and local responses. It exits when the command receiver closes.
- `process_command` dispatches `HealChannelCommand::Start`, `Query`, and `Cancel`.
- `process_start_request` converts a channel request, submits it with `HealManager::submit_heal_request`, returns `HealAdmissionResult`, and broadcasts an admission response.
- `process_query_request` calls `HealManager::get_task_report_for_path` and maps internal statuses to the external summaries `running`, `finished`, or `stopped`.
- `process_cancel_request` cancels either by explicit client token or, if token is empty, by heal path.
- `convert_to_heal_request` maps channel fields into `HealType`, `HealPriority`, and `HealOptions`.
- `publish_response` sends to the local unbounded channel and calls `publish_heal_response`.
- `get_response_sender` exposes a clone of the local response sender.

## Control flow

The main loop receives a command, logs it, and lets command-specific handlers send the oneshot response. Start requests are converted before manager submission. Conversion failures produce an immediate error oneshot plus a failed broadcast. Successful manager admission sends `Ok(admission)` to the caller and publishes a response whose `data` contains an ASCII `admission=...,reason=...` string; queue-full or dropped admissions are treated as unsuccessful broadcast responses even though manager submission itself returned `Ok`.

Query requests are path-token bound. Active or queued tasks produce `running`, completed tasks produce `finished`, cancelled/timeout/failed tasks produce `stopped` with an error/detail string, and a missing task is treated as `finished` with no result items. A mismatched token for a path that still has a task is reported as `invalid heal client token`.

Cancel requests use token precedence when the token is non-empty. Empty-token cancellation cancels all queued or active tasks matching the path and treats a missing path as already stopped, which gives idempotent cancel behavior for path-level admin calls.

## State and persistence behavior

This file has no durable state. Its persistent effects come through `HealManager` and through the global heal-channel response publisher. The local response channel is in-memory, unbounded, and only used by this processor instance to observe responses. Query response result items are drawn from active task state or the manager's short-lived completed-task cache.

## Dependencies and integration points

The file depends on `HealManager`, `HealTaskReport`, internal `task` types, and `utils::normalize_set_disk_id`. It integrates with `rustfs_common::heal_channel` for command/request/response/admission/scan-mode types and global response publication. It serializes query payloads with `serde_json`, returns object-level result items from `rustfs_madmin::heal_commands`, and uses structured `tracing` fields for heal-channel observability.

## Risks and edge cases

- `force_start` deliberately affects admission only. The comment warns against interpreting it as `remove_corrupted=true`, because admin clients may pass force start with remove false.
- Disk requests become `HealType::ErasureSet` with an empty bucket list; callers or later storage logic must populate buckets for actual erasure-set healing.
- Query treats `TaskNotFound` as finished. This is useful for client polling after completion but can hide lost status once completed-task retention expires.
- Local response delivery failure is logged but does not block global broadcast.
- Unbounded local response buffering can grow if responses are produced faster than the processor drains them.
- Query JSON serialization failure is propagated as `Serialization`.

## Test signals

The test module uses a `MockStorage` and covers conversion behavior, start admission paths, query reporting for missing/queued/wrong-token/empty-path cases, cancel by token, cancel by path, idempotent unknown-path cancel, and unknown-token cancel errors. Additional useful tests would cover broadcast failure behavior, invalid disk-id conversion, and `force_start` preserving non-destructive options.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/channel.rs -->
