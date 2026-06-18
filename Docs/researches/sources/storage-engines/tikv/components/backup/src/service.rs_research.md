# sources/storage-engines/tikv/components/backup/src/service.rs

## Purpose
Implements the gRPC `Backup` service facade for TiKV backup. It translates client RPC streams into internal backup tasks, snapshot-backup stream handling, and legacy pending-admin checks. The file is intentionally thin around scheduling and stream lifecycle; storage scanning and disk snapshot logic live in sibling modules.

## APIs, Types, And Functions
`Service<H: SnapshotBrHandle>` owns a `Scheduler<Task>`, disk snapshot environment, and `abort_last_req` slot. `Service::new` wires those dependencies. The `Backup` trait implementation exposes `check_pending_admin_op`, `backup`, and `prepare_snapshot_backup`. `check_pending_admin_op` calls `SnapshotBrHandle::broadcast_check_pending_admin` and forwards responses to a server stream. `backup` builds a `Task` from `BackupRequest`, schedules it, and streams `BackupResponse` values from an unbounded channel. `prepare_snapshot_backup` creates a `StreamHandleLoop`, aborts any previous stream, and runs the duplex stream on the snapshot async runtime.

## Control Flow
For normal backup, request validation happens in `Task::new`; schedule errors are converted to gRPC status and sent via `sink.fail`. Once scheduled, the response channel is drained into the RPC sink. If stream sending fails, the captured cancellation `AtomicBool` is set so the worker can stop. For snapshot backup, the newest stream replaces the previous one by aborting the stored `AbortHandle`, then `StreamHandleLoop::run` owns request processing until completion or unrecoverable error.

## State And Persistence
No persistent data is written here. Runtime state is the shared scheduler, snapshot environment, and `abort_last_req` mutex. Cancellation is communicated through task-local atomics and future abort handles. The use of an unbounded channel is called out as a TODO and can hold arbitrary responses if a client stops reading.

## Dependencies And Integration Points
Depends on `grpcio`, `kvproto::brpb`, `futures` channels/streams, TiKV worker scheduling, and raftstore snapshot backup handles. It integrates with `crate::Task`, `crate::disk_snap::Env`, and `StreamHandleLoop`. RPC clients observe only protobuf responses and gRPC errors, while internal backup workers observe scheduled `Task`s.

## Risks And Test Signals
Important risks are cancellation timing, unbounded response buffering, and correctness of "last snapshot stream wins" behavior. The included `test_client_stop` starts a real gRPC server and verifies dropped client streams do not panic and do set task cancellation. The compatibility method `check_pending_admin_op` is not deeply tested here because the test handle deliberately panics if invoked.
