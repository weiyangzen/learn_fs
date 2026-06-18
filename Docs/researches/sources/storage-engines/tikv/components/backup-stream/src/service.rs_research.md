# sources/storage-engines/tikv/components/backup-stream/src/service.rs

## Purpose
`service.rs` exposes the backup-stream gRPC service for operational control and checkpoint queries. It adapts `kvproto::logbackuppb::LogBackup` RPCs into internal backup-stream endpoint tasks, returning flush results, per-region checkpoint state, and a server-streaming subscription for checkpoint flush events.

The file is intentionally thin: it contains no backup data persistence itself. Its importance is in the RPC-to-scheduler boundary, where client-visible commands enter the endpoint event loop and where endpoint callback results are translated back to protobuf responses.

## Important APIs, Types, And Functions
`BackupStreamGrpcService` owns a `tikv_util::worker::Scheduler<Task>` and is `Clone`, allowing gRPC service clones to schedule work into the backup-stream endpoint. `BackupStreamGrpcService::new()` constructs the wrapper.

`id_of(region: &Region) -> RegionIdentity` extracts region id and epoch version into the protobuf identity used by checkpoint responses. `impl From<RegionIdWithVersion> for RegionIdentity` converts checkpoint-manager not-found keys into the same protobuf shape.

The `LogBackup` implementation provides three RPCs. `flush_now()` schedules `Task::ForceFlush(TaskSelector::All, tx)` with an mpsc response channel and streams all internal per-task flush results into a single `FlushNowResponse`. `get_last_flush_ts_of_region()` converts request region identities into a `HashSet<(id, epoch_version)>`, schedules `Task::RegionCheckpointsOp(RegionCheckpointOperation::Get(...))`, and fills `GetLastFlushTsOfRegionResponse` in the callback. `subscribe_flush_event()` schedules `RegionCheckpointOperation::Subscribe(sink)` in non-test builds and intentionally panics under unit tests if invoked.

## Control Flow
`flush_now()` logs the peer, creates a response accumulator and a one-element mpsc channel, then schedules a force flush for all tasks. If scheduling fails, it immediately sends an INTERNAL gRPC failure with a busy/shutdown message. On successful scheduling, it spawns an async response task on the gRPC context. That task receives all items until the endpoint closes the channel, converts each item into `FlushResult` with success boolean, optional error text, and task name, then sends `sink.success(resp)`.

`get_last_flush_ts_of_region()` takes ownership of the request regions, maps them into a set, and builds an endpoint callback. The callback converts each `GetCheckpointResult` variant: `Ok` carries the returned region and checkpoint; `NotFound` carries the requested id/version and error; `EpochNotMatch` carries the actual region and error. The callback uses `tokio::spawn()` to send the unary response, so the endpoint task does not block on gRPC sink completion.

`subscribe_flush_event()` logs the client id. In production it schedules a region-checkpoint subscription operation containing the server-streaming sink; the checkpoint manager/endpoint owns subsequent stream writes.

## State And Persistence Behavior
`BackupStreamGrpcService` keeps only a scheduler handle. It does not cache responses, checkpoint state, or subscription state. Persistence behavior is delegated to endpoint tasks, checkpoint manager, router flush logic, and metadata storage. The RPC methods are asynchronous boundaries: a scheduled task may fail later and must report through the provided channel or callback.

For `flush_now()`, response completion depends on the endpoint dropping the mpsc sender after sending all task results. If the endpoint stalls or forgets to close the sender, the gRPC request remains pending. For checkpoint queries, response shape preserves both successful checkpoints and per-region errors so clients can distinguish absence and epoch mismatch without out-of-band state.

## Dependencies And Integration Points
The service depends on `grpcio`, `kvproto::logbackuppb`, `kvproto::metapb::Region`, `tikv_util` logging and worker scheduler, endpoint task types, `RegionCheckpointOperation`, `RegionSet`, checkpoint-manager result types, and `TaskSelector`. It is integrated into TiKV's gRPC service registration outside this file.

External clients observe the protobuf contracts: `FlushNowRequest/Response`, `FlushResult`, `GetLastFlushTsOfRegionRequest/Response`, `RegionCheckpoint`, `RegionIdentity`, and `SubscribeFlushEventRequest/Response`. Internally, the endpoint must understand `Task::ForceFlush` and `Task::RegionCheckpointsOp`.

## Risks And Edge Cases
The main risk is scheduler failure. `flush_now()` handles schedule errors with an explicit gRPC INTERNAL status, but `get_last_flush_ts_of_region()` and `subscribe_flush_event()` use `try_send!`; depending on macro behavior, schedule failures are logged or converted outside the local function body rather than building a typed gRPC error here.

`flush_now()` accumulates all task flush results in memory before replying. That is acceptable for the expected number of backup tasks but is not streaming. It also clones the response for logging on sink failure. The mpsc channel size is one, so endpoint result production can be backpressured by the response task.

`get_last_flush_ts_of_region()` collapses duplicate requested `(id, epoch_version)` pairs into a set, so duplicate request entries do not produce duplicate response entries. Response ordering follows endpoint result iteration, not request order. The callback spawns with `tokio::spawn()` rather than `ctx.spawn()`, so runtime availability and shutdown behavior matter.

`subscribe_flush_event()` carries a long-lived gRPC sink into endpoint state. Tests deliberately panic if the service path is used, which indicates subscription behavior is expected to be tested below the gRPC layer.

## Test Signals
This file has no local test module beyond the `#[cfg(test)] panic` guard in `subscribe_flush_event()`. Its behavior is indirectly tested through endpoint and checkpoint-manager tests that schedule `Task::ForceFlush` and `RegionCheckpointOperation` variants. Useful direct tests would use a dummy scheduler to assert that `flush_now()` schedules `ForceFlush(All)`, schedule failure maps to INTERNAL, checkpoint results convert each `GetCheckpointResult` variant correctly, duplicate checkpoint request regions are deduplicated, and subscription scheduling transfers the sink in non-test builds.
