# sources/storage-engines/tikv/components/test_backup/src/disk_snap.rs

## Purpose
This file provides a test harness for snapshot-backup preparation over raftstore disk snapshots. It starts per-store backup gRPC services, registers a `PrepareDiskSnapObserver` with raftstore coprocessor hosts, and wraps the streaming `PrepareSnapshotBackup` protocol in ergonomic test utilities.

## Important APIs, Types, And Functions
`Node` stores an optional gRPC `Server`, the shared `PrepareDiskSnapObserver` rejector, and a backup client. `Suite` owns a `test_raftstore` server cluster, node map, and shared gRPC environment. `Suite::new_with_cfg` builds a cluster, registers observers before `cluster.run`, then starts backup services for each store. `start_backup` constructs a `backup::Service` with a disk-snapshot environment around the store router and rejector. `try_split` and `split` drive raftstore region splits for tests.

`PrepareBackup` wraps a duplex streaming sink/receiver pair. `prepare` sends `UpdateLease`, `wait_apply` sends a `WaitApply` request and waits until every requested region emits `WaitApplyDone`, `send_wait_apply` separates send from receive, `send_finalize` sends `Finish` and returns whether the last lease was valid, and `next`/`try_next` expose response polling. Assertion helpers validate raft command success or expected failures.

## Control Flow And State
The harness mutates cluster topology and streaming backup state. `prepare_backup` opens a stream to one node's backup service; calls then send typed protocol requests and synchronously block on futures. `wait_apply` tracks a `HashSet` of region IDs and removes each successful completion. `send_finalize` tolerates already-finished RPCs and uses a two-second timeout while draining responses.

## Persistence And Integration Points
Integration points include `backup::disk_snap::Env`, raftstore routers, `PrepareDiskSnapObserver`, gRPC backup service/client generation from `brpb`, and `test_raftstore` cluster control. Persistence is indirect through raftstore disk snapshot and region state rather than local files in this module.

## Risks And Test Signals
This harness is intentionally timing-sensitive: waits use blocking futures and fixed timeout behavior. `crate_node` appears misspelled but is internal. Stream finalization assumes an `UpdateLeaseResult` event appears before timeout. The assertion helpers are track-caller annotated and are the main test signals for success, generic failure, or failure message contents.
