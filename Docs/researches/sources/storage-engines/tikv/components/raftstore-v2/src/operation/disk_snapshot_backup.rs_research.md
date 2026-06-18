# sources/storage-engines/tikv/components/raftstore-v2/src/operation/disk_snapshot_backup.rs

## Purpose
Provides a placeholder `SnapshotBrHandle` implementation for raftstore-v2, explicitly reporting that snapshot backup is unsupported.

## Important APIs, Types, And Functions
`UnimplementedHandle` is a clone/copy zero-sized type implementing `raftstore::store::snapshot_backup::SnapshotBrHandle`. The implemented methods are `send_wait_apply`, `broadcast_wait_apply`, and `broadcast_check_pending_admin`. All return `crate::Error::Other` with the shared reason string.

## Control Flow
There is no operational backup flow. Any snapshot-backup caller using this handle immediately receives an error that names the unsupported method and notes that raftstore-v2 does not support snapshot backup yet.

## State And Persistence Behavior
The type has no state and performs no persistence, message routing, or channel sends. The `broadcast_check_pending_admin` method accepts an `UnboundedSender<CheckAdminResponse>` but deliberately does not use it.

## Dependencies And Integration Points
Depends on the snapshot backup trait and request/response protobuf types from raftstore/kvproto. It is an integration shim that lets the broader store compile while making unsupported raftstore-v2 snapshot BR behavior explicit at runtime.

## Risks And Edge Cases
The main risk is operational: callers must surface this unsupported error clearly and avoid assuming snapshot backup works for raftstore-v2. Since every method fails synchronously, no partial state is created.

## Test Signals
There are no local tests. Expected signal is the exact error path from callers invoking snapshot backup APIs under raftstore-v2.
