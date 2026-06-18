# sources/storage-engines/tikv/src/server/service/kv.rs

## Purpose
`kv.rs` implements TiKV's public `Tikv` gRPC service. It is the transport-facing bridge from kvproto RPCs into storage transaction commands, raw KV commands, coprocessor endpoints, raft message ingestion, snapshot scheduling, region split/check-leader helpers, health feedback, and batch-command multiplexing. The file is on TiKV's critical path because it performs request validation, request-source/resource-control accounting, async dispatch, response shaping, gRPC stream management, and raft/snapshot backpressure decisions.

## Important APIs, Types, and Functions
`Service<E, L, F>` is the main service object, parameterized by the storage engine, lock manager, and API-version key format. It holds cluster and store ids, `Storage`, GC worker, coprocessor v1/v2 endpoints, snapshot and check-leader schedulers, gRPC thread-load tracking, proxy forwarding, resource-group manager, health controller, health feedback sequence state, and a raft message filter.

`RaftGrpcMessageFilter` abstracts rejection policy for incoming raft append and snapshot traffic. `DefaultGrpcMessageFilter` rejects `MsgAppend` only when memory pressure crosses `reject_messages_on_memory_ratio`, while failpoints can force raft append or snapshot rejection.

The `handle_request!` macro implements most unary methods. It rejects cluster-id mismatches, optionally forwards through `Proxy`, consumes resource-control penalty, records resource-group counters, awaits a `future_*` helper, sets total RPC time for selected responses, sends the unary result, and records success/failure metrics. `reject_if_cluster_id_mismatch!` and `set_total_time!` are the related validation/timing helpers.

Hand-written service methods cover flashback, coprocessor, raw coprocessor, unsafe destroy range, streaming coprocessor, raft streams, batch raft streams, snapshot streams, tablet snapshots, split region, batch commands, check-leader, store safe ts, lock-wait dump, and health feedback. `handle_raft_message` validates destination store id, applies raft-append rejection policy, reports rejected messages, and feeds accepted messages to `RaftExtension`.

`handle_batch_commands_request`, `response_batch_commands_request`, `MeasuredSingleResponse`, `MeasuredBatchResponse`, `GrpcRequestDuration`, and `collect_batch_resp` implement the bidirectional batch command protocol. `HealthFeedbackAttacher` injects store slow-score feedback into batch responses on demand or at an interval.

The `future_*` functions translate kvproto request types into storage APIs. Important families include transactional read helpers (`future_get`, `future_scan`, `future_batch_get`, `future_buffer_batch_get`, `future_scan_lock`), raw KV helpers (`future_raw_get`, `future_raw_batch_get`, `future_raw_put`, `future_raw_batch_put`, `future_raw_delete`, `future_raw_batch_delete`, `future_raw_scan`, `future_raw_batch_scan`, `future_raw_delete_range`, `future_raw_get_key_ttl`, `future_raw_compare_and_swap`, `future_raw_checksum`), flashback helpers, coprocessor helpers, and `txn_command_future!`-generated transaction command futures for prewrite, pessimistic lock/rollback, commit, cleanup, heartbeat, check txn status, check secondary locks, MVCC inspection, flush, and resolve/batch rollback.

## Control Flow
Most unary RPCs enter a generated `handle_request!` method. The request context is checked against `Service.cluster_id`, then the request may be forwarded by proxy. Resource-group metadata is observed before a storage future is created. The async task awaits the future, decorates timing fields where supported, sends the response via `UnarySink`, records histogram/source metrics, and maps network/storage errors to log counters.

Storage futures are response adapters around `Storage` methods. Read paths usually create a global request tracker, record request protobuf size, translate raw keys into `txn_types::Key`, await storage, extract region errors ahead of key errors, write scan/time/RU details, and remove the tracker. Write-like APIs use `paired_future_callback`: a command is scheduled synchronously, then the async future awaits the callback result before constructing the protobuf response.

The transaction-command macro centralizes conversion from request protobuf into typed storage commands. It schedules the command through `storage.sched_txn_command`, extracts region errors first, then command-specific branches fill fields such as `min_commit_ts`, `one_pc_commit_ts`, pessimistic-lock result arrays, commit version, lock TTL, txn action, secondary lock status, MVCC info, and per-key errors. It also writes scan/write/time/RU tracker details for most transaction commands.

Raft ingestion is stream-oriented. `raft` reads individual `RaftMessage`s; `batch_raft` reads `BatchRaftMessage`s, measures receive delay from `last_observed_time`, and iterates contained messages. Both use metadata to count messages by source store, reject only `StoreNotMatch` as a stream-breaking error, and otherwise keep the stream open until peer shutdown or transport error.

Snapshot and tablet-snapshot RPCs do not process bytes locally. They wrap the gRPC stream/sink into `SnapTask::Recv` or `SnapTask::RecvTablet` and schedule it on the snapshot worker. Rejection occurs before scheduling if the raft message filter refuses snapshots or if the scheduler is full.

`batch_commands` splits into two tasks. The request task reads each `BatchCommandsRequest`, creates a request batcher, dispatches or batches individual subrequests, and commits any compatible get/raw-get batches. Each subrequest response is sent through an internal channel as `MeasuredSingleResponse`. The response task uses `BatchReceiver` to coalesce responses up to `GRPC_MSG_MAX_BATCH_SIZE`, records per-command elapsed and wait times, attaches transport load and health feedback, then sends a `BatchCommandsResponse` over the duplex sink.

## State and Persistence Behavior
`Service` itself owns mostly process-local routing and accounting state. Persistent data changes happen through `Storage`, `GcWorker`, `RaftExtension`, and snapshot worker integrations rather than direct disk writes in this file. Transactional and raw write futures schedule storage commands that later persist through raftstore/engine layers. Flashback is a special multi-step operation: prepare starts engine flashback state and schedules a prewrite-like command to block resolved-ts advancement; execute schedules the flashback transaction command and only calls `end_flashback` after the data operation succeeds.

Raft messages are persisted by downstream raftstore after `RaftExtension::feed`. This file can drop or reject inbound raft traffic under memory pressure, but it does not append logs itself. Snapshot RPCs schedule receive work; persistence of snapshot files and raft feed happen in `snap.rs`.

Mutable in-service state includes the atomic health feedback sequence, scheduler handles, and cloned counters/load pools. `HealthFeedbackAttacher` keeps per-stream last-feedback time and generates monotonically increasing feedback sequence numbers through the shared `AtomicU64`.

## Dependencies and Integration Points
The file integrates with `kvproto` request/response types, `grpcio`, `Storage<E, L, F>`, lock managers, API-version key encoding, coprocessor v1 and v2 endpoints, raftstore `RaftExtension`, snapshot worker tasks, check-leader scheduler, GC worker, resource-control manager, health controller, request trackers, TiKV metrics, failpoints, and proxy forwarding macros.

The public re-exports in `service/mod.rs` expose `Service` as `KvService`, raft message filters, batch-command request/response aliases, measured response structures, and flashback futures to other server modules/tests.

## Risks and Edge Cases
Cluster-id validation is repeated in unary and batch paths; missing it on a hand-written method can admit cross-cluster requests. Batch-command cluster-id mismatch returns both an in-band response item and a gRPC invalid-argument error, so client behavior depends on stream handling. Resource-group counter labels currently use the same resource group name twice, which may be intentional metric schema behavior but is worth checking before changing.

The raft rejection path must only reject traffic that raftstore can recover from. `StoreNotMatch` intentionally breaks the stream so the sender can resolve the correct address from PD, while other raft feed errors are swallowed. The memory-based append rejection policy depends on global high-water memory reporting and memory trace counters for raft messages, entry cache, and applying entries.

Several methods remain `unimplemented!` (`kv_import`, batch coprocessor, MPP dispatch/cancel/connection) or explicitly return unimplemented (`kv_gc`/`future_gc`). `unsafe_destroy_range` uses assertions to reject empty boundaries; malformed external requests can panic rather than return a protobuf error. Flashback sequencing is sensitive because prepare locks a region and execute must only end flashback after successful modification.

The tracker lifecycle is manual in several futures. Most paths remove trackers explicitly or via `defer!`; early returns or future rewrites must preserve removal to avoid tracker leaks and incorrect RU/scan metrics. Batch response timing is measured at collection time, so channel backpressure affects `kv_grpc_wait_time_ns`.

## Test Signals
Local tests cover RU v2 fields for `future_get`, `future_batch_get`, and `future_prewrite`; `poll_future_notify` behavior when futures are completed from another thread or polled by a slow poller; and `HealthFeedbackAttacher` interval/on-demand behavior, sequence increments, slow-score propagation, and multiple `GetHealthFeedback` responses in one batch. Compile coverage also validates the large RPC-to-future mapping. Broader behavioral coverage should come from integration tests around gRPC batch commands, raft stream rejection, snapshot scheduling, cluster-id mismatch, and flashback error paths.
