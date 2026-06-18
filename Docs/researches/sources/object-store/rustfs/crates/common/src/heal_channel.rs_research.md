# sources/object-store/rustfs/crates/common/src/heal_channel.rs

## Purpose
`heal_channel.rs` defines shared types and global messaging helpers for RustFS heal operations, plus lifecycle and replication rule helper functions used to decide whether healing-related work is active for prefixes.

## Important APIs, Types, and Functions
Constants include `HEAL_DELETE_DANGLING`, `RUSTFS_RESERVED_BUCKET`, and `RUSTFS_RESERVED_BUCKET_PATH`. Domain enums include `HealItemType`, `DriveState`, `HealScanMode`, `HealAdmissionDropReason`, `HealAdmissionResult`, and `HealChannelPriority`. DTOs are `HealOpts`, `HealChannelRequest`, and `HealChannelResponse`. `HealChannelCommand` has `Start`, `Query`, and `Cancel` variants with oneshot response senders. Global channel APIs are `init_heal_channel`, `get_heal_channel_sender`, `send_heal_command`, `send_heal_request_with_admission`, `send_heal_request`, `query_heal_status`, `cancel_heal_task`, `send_heal_disk`, `publish_heal_response`, and `subscribe_heal_responses`. Helper constructors create requests and responses. Rule helpers include `lc_has_active_rules` and `rep_has_active_rules`.

## Control Flow
`init_heal_channel` creates one unbounded mpsc command channel and stores the sender in a `OnceLock`; subsequent calls fail. Command send helpers package a command with a oneshot sender, send through the global channel, and await the response. Admission results are translated to `Ok(())` for accepted/merged or string errors for full/dropped. Broadcast responses use a lazily initialized broadcast channel of size 1024; `publish_heal_response` ignores the returned receiver count and reports success even with no subscribers. Lifecycle rule checks skip disabled rules, match prefixes, then look for expiration, noncurrent expiration, transitions, or delete-marker settings. Replication rule checks skip disabled rules and apply recursive/non-recursive prefix matching.

## State and Persistence Behavior
The command sender and response broadcaster are process-global `OnceLock`s. Requests/responses are in-memory channel messages; no persistence is performed. Request ids are generated with UUIDs in constructors. Heal options are serializable/deserializable and use serde renames for admin/API compatibility.

## Dependencies and Integration Points
Uses `tokio::sync::{mpsc, oneshot, broadcast}`, `uuid`, `serde`, and `s3s::dto` lifecycle/replication types. This file is a boundary between admin/API code that submits heal operations and the background heal manager that consumes commands.

## Risks and Edge Cases
The command channel is unbounded, so backpressure must be implemented by the consumer/admission policy, not the channel. The global command sender cannot be reset, which affects tests and process lifecycle. `HealScanMode` supports numeric and string deserialization, but invalid values fail. `publish_heal_response` discards broadcast send errors and always returns `Ok(())`; lagged subscribers must handle broadcast receiver errors. Prefix matching in lifecycle/replication helpers is subtle and may over/under-match if S3 rule semantics change.

## Test Signals
Unit tests validate stable admission labels/reasons and `is_admitted`. They also verify that a subscriber receives published heal responses and that publishing without subscribers is treated as success.
