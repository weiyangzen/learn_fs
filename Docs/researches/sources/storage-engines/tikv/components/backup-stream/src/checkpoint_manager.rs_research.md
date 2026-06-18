# sources/storage-engines/tikv/components/backup-stream/src/checkpoint_manager.rs

## Purpose
`checkpoint_manager.rs` tracks per-region backup-stream flush checkpoints, freezes resolved timestamps around flush boundaries, notifies subscribers of flush events, serves checkpoint queries, and implements flush observers for PD service safepoints and checkpoint V3 metadata integration.

## Important APIs, Types, And Functions
- `CheckpointManager` stores `checkpoint_ts`, `frozen_resolved_ts`, `resolved_ts`, and an optional subscription-manager sender.
- `SubscriptionManager` owns gRPC/server-stream subscribers and processes `SubscriptionOp::{Add, Emit, Inspect}`.
- `GetCheckpointResult` returns `Ok`, `NotFound` with a not-leader-style protobuf error, or `EpochNotMatch`.
- `RegionIdWithVersion` and `LastFlushTsOfRegion` identify/query checkpoint state.
- `FlushObserver` defines async hooks `before`, `after`, and optional `rewrite_resolved_ts`.
- `BasicFlushObserver` updates a PD service safe point and metrics after a flush.
- `CheckpointV3FlushObserver` sends region checkpoint flush tasks, reads global checkpoint metadata, caches it per task, and delegates PD safepoint updates to a baseline observer.

## Control Flow
Resolved-ts updates enter through `resolve_regions`, which updates `resolved_ts` by region id. Before a data flush, `freeze` moves `resolved_ts` into `frozen_resolved_ts` so later incoming data cannot advance the currently flushing checkpoint. After files are fully written, `flush_and_notify` optionally applies final `last_dive` checkpoints, replaces durable `checkpoint_ts` with the frozen map, and emits `FlushEvent`s to subscribers. `get_from_region` validates both region id presence and epoch version.

The subscription manager runs an async loop. New subscribers are stored under generated UUIDs. Event emission chunks responses in groups of 1024 events, feeds and flushes each sink, and removes subscribers whose stream errors. Adding a subscriber also emits current checkpoint state as initial data.

`update_ts` only replaces existing entries when the incoming region epoch is newer, or the same epoch has a newer checkpoint. Older checkpoints are logged but ignored unless paired with newer epoch behavior.

## State And Persistence Behavior
The manager state is in memory. It represents flushed external-storage durability, not raw resolved-ts progress. PD service safepoints written by `BasicFlushObserver` persist outside the process with a 2-hour TTL at `rts - 1`. Checkpoint V3 observer reads global checkpoint metadata through `MetadataClient` and schedules region checkpoint flush operations through the backup-stream task scheduler.

## Dependencies And Integration Points
The file integrates with `endpoint.rs` for checkpoint manager ownership and observer creation, `subscription_track::ResolveResult`, backup-stream `Task` and `RegionCheckpointOperation`, metadata store/client traits, PD client, grpcio streaming sinks, `kvproto` error/logbackup/metapb messages, metrics, tracing instrumentation, and `tikv_util` scheduler/logging helpers.

## Risks And Edge Cases
- Subscription channel capacity is finite; `notify` drops events when `try_send` fails.
- `add_subscriber` sends `Add` before initial `Emit`, so initial events are broadcast through the manager rather than targeted only to the new subscriber.
- `flush_and_notify` replaces `checkpoint_ts` with the frozen set; if no new resolved regions were frozen, previously queryable checkpoints disappear. Tests document this behavior.
- `sync_with_subs_mgr` unwraps `manager_handle` and is test/support oriented.
- `CheckpointV3FlushObserver` caches global checkpoint per task and can become stale unless cache invalidation is handled by task lifecycle.

## Test Signals
Inline tests cover successful subscription notification, subscriber removal on RPC failure, freeze/flush state transitions, checkpoint epoch/version update rules, last-dive override behavior, and PD service safepoint update by `BasicFlushObserver`. Integration references in `endpoint.rs` exercise manager wiring.
