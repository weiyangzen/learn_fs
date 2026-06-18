# sources/storage-engines/tikv/components/raftstore/src/store/snapshot_backup.rs

## Purpose

Coordinates disk snapshot backup preparation with raftstore peers. It provides a router-facing handle for waiting until peers have applied logs, a coprocessor observer that temporarily rejects ingests, selected admin commands, and leader transfers while disk snapshot backup is prepared, and syncer/state types that report wait-apply success or abort back to backup callers.

## Important APIs, Types, And Functions

`SnapshotBrWaitApplyRequest` wraps a `SnapshotBrWaitApplySyncer`, an optional expected region epoch, and a flag that aborts on term changes. `relaxed` waits only to the last index; `strict` also checks epoch and term/commit safety. `SnapshotBrHandle` abstracts `send_wait_apply`, `broadcast_wait_apply`, and `broadcast_check_pending_admin`; the `Arc<Mutex<RaftRouter>>` implementation sends `SignificantMsg::SnapshotBrWaitApply` or `CheckPendingAdmin` through raftstore routing and increments wait-apply metrics.

`PrepareDiskSnapObserver` is a coprocessor with an atomic lease deadline (`before`) and initialized flag. It registers query, admin, and transfer-leader observers, exposes `remained_secs`, `allowed`, `update_lease`, and `reset`, and returns `CopError::RequireDelay` while backup suspension is active. `SnapshotBrWaitApplySyncer` owns a shared `SyncerCore` with `report_id` and a oneshot sender. `SyncReport` reports success or an `AbortReason` (`EpochNotMatch`, `StaleCommand`, or `Duplicated`). `SnapshotBrState::WaitLogApplyToLast` is peer FSM state for waiting until a target index is applied under an optional valid term.

## Control Flow

Backup control code creates a wait-apply request and sends it to one region or broadcasts it. Peer FSM handlers receive the significant message, validate epoch/term requirements, set `SnapshotBrState::WaitLogApplyToLast`, and eventually drop the syncer when the target apply index is reached. `SyncerCore::Drop` sends a success `SyncReport` when the last syncer reference is dropped without abort. Calling `SnapshotBrWaitApplySyncer::abort` takes the oneshot sender immediately, sends an abort report, records the corresponding metric, and makes later drops log that wait apply was aborted.

The prepare observer flow is lease-based. `update_lease` extends the suspension deadline if the new deadline is later, updates a gauge, and records create or renew metrics. `allowed` returns true when no lease exists; when the stored deadline has expired it atomically resets the deadline to zero, updates metrics, and allows traffic again. While the lease is active, query proposals containing `ingest_sst`, admin proposals for split, prepare merge, change peer, witness switch, compact log, and transfer leader requests are rejected with `RequireDelay`.

## State And Persistence Behavior

All state is in memory. The suspension lease is an atomic coarse epoch-second deadline, not persisted. Syncer completion is reference-counted via `Arc<Mutex<SyncerCore>>`; success is signaled by drop of the final clone, while abort consumes the oneshot sender. Metrics record sent/finished/abort events and lease lifecycle. No snapshot data is read or written here; this file protects the raftstore state while other BR components prepare disk snapshots.

## Dependencies And Integration Points

Depends on raftstore `RaftRouter`, `PeerMsg`, `SignificantMsg`, and metrics; `CoprocessorHost` observer registries; query/admin/transfer-leader observer traits; tokio oneshot channels; futures unbounded channels for pending-admin checks; and kvproto admin/epoch/check response types. Peer FSM code consumes `SnapshotBrState` and `SnapshotBrWaitApplyRequest`, while external backup orchestration uses `SnapshotBrHandle` and `PrepareDiskSnapObserver`.

## Risks

The observer deliberately blocks important raftstore operations and can affect transactional workloads if the lease is too long or not reset. `allowed` uses coarse monotonic seconds, so very short leases are approximate. Query rejection marks `cx.bypass = true` for ingests and rejects the entire command batch rather than just the ingest request. `CompactLog` is blocked to preserve logs for restore, which can increase log retention pressure. Syncer success depends on all peer-held clones being dropped; leaks or forgotten state transitions would delay the oneshot result. Duplicate or stale wait-apply commands must abort cleanly to avoid callers believing an unsafe snapshot point is ready.

## Test Signals

This file has no local `#[cfg(test)]` module. Test signals are expected from raftstore peer FSM and BR integration tests that send `SnapshotBrWaitApply`, exercise epoch/term mismatch aborts, wait apply to target index, duplicate requests, pending admin checks, and coprocessor rejection under active backup leases. Operational metrics `SNAP_BR_WAIT_APPLY_EVENT`, `SNAP_BR_LEASE_EVENT`, `SNAP_BR_SUSPEND_COMMAND_LEASE_UNTIL`, and `SNAP_BR_SUSPEND_COMMAND_TYPE` are important runtime signals.
