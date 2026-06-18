# sources/storage-engines/tikv/components/backup/src/disk_snap.rs

## Purpose
This module implements the server-side loop for preparing disk snapshot backup over a bidirectional gRPC stream. It manages snapshot backup lease updates, wait-apply requests for regions, reset/finish semantics, stream aborts, and conversion of raftstore/snapshot preparation failures into either stream-level RPC failures or protobuf region errors.

## Important APIs, Types, And Functions
`Env<SR>` carries a `SnapshotBrHandle`, a `PrepareDiskSnapObserver` rejector/lease gate, an active stream counter, and either an injected Tokio handle or a default runtime. `ResultSink` wraps `grpcio::DuplexSink<PResp>` and sends success responses, protobuf error responses, or aborts the stream. Internal `Error` variants distinguish uninitialized observer, expired lease, wait-apply aborts, and raftstore errors. `HandleErr` decides whether an error is returned as a gRPC status or a `errorpb::Error`. `StreamHandleLoop<SR>` owns pending wait-apply futures and an abortable pending future; `run` drives the request/response loop.

## Control Flow
Clients send `UpdateLease`, `WaitApply`, and `Finish` requests. `UpdateLease` validates initialization and extends the observer lease, returning whether the previous lease was valid. `WaitApply` first checks that the observer is initialized and currently rejecting normal writes; then it sends strict wait-apply requests to raftstore for each region and stores futures in `pending_regions`. `next_event` races incoming stream items, completed wait-apply futures, and server abort. Completed wait-apply futures emit `WaitApplyDone` responses or region errors. `Finish` resets the observer, sends a final lease result, closes the sink, and exits.

## State And Persistence Behavior
State is in-memory: active stream count, observer lease/rejector state, and pending region futures. Dropping `StreamHandleLoop` decrements `active_stream`. There is no durable persistence in this file. The lease state controls whether wait-apply requests are meaningful; expired leases abort the stream with `FAILED_PRECONDITION`.

## Dependencies And Integration Points
The module integrates with raftstore snapshot backup APIs (`PrepareDiskSnapObserver`, `SnapshotBrHandle`, `SnapshotBrWaitApplyRequest`, `SnapshotBrWaitApplySyncer`, `AbortReason`), `kvproto::brpb` prepare snapshot messages, `errorpb` region errors, grpcio duplex streaming, Tokio runtime/oneshot, and TiKV utility runtime/thread naming.

## Risks And Edge Cases
If the observer is uninitialized, the stream aborts as unavailable. If the lease expires, further wait-apply attempts abort the stream because the backup-side write rejection window is no longer valid. Wait-apply abort reasons are mapped best-effort; epoch mismatch and stale command receive structured fields, other reasons become messages only. Pending futures are scanned linearly and `swap_remove` changes completion order, which is acceptable for region wait responses but should be noted.

## Test Signals
No inline tests are present in this file. Behavior is likely exercised through service-level disk snapshot backup tests elsewhere. Important observable signals are active stream count, gRPC status codes, response event types, and errorpb fields for epoch mismatch or stale command.
