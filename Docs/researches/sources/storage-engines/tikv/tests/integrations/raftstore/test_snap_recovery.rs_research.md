# sources/storage-engines/tikv/tests/integrations/raftstore/test_snap_recovery.rs

## Purpose
This file tests snapshot backup/recovery coordination messages that must wait for pending raft apply work before reporting safe progress. It focuses on detecting pending admin commands and waiting for a leader peer to finish applying inflight log entries.

## Important APIs, Types, and Functions
It uses `PeerMsg::SignificantMsg`, `SignificantMsg::CheckPendingAdmin`, `SignificantMsg::SnapshotBrWaitApply`, `SnapshotBrWaitApplyRequest`, `SnapshotBrWaitApplySyncer`, `SyncReport`, and the store router obtained from `cluster.sim.wl().get_router(1)`. It also uses `RegionPacketFilter` to block `MsgAppendResponse` messages, plus `block_on_timeout` and oneshot/mpsc channels for asynchronous assertions.

## Control Flow
`test_check_pending_admin` starts a three-node server cluster, transfers leadership, writes data, then blocks append responses to the leader so an async add-peer admin request remains pending. It broadcasts `CheckPendingAdmin` and expects `has_pending_admin == true`, clears filters, waits, and expects false. `test_snap_wait_apply` similarly blocks append responses, issues an async put, broadcasts `SnapshotBrWaitApply`, expects timeout while apply is stuck, then clears filters and expects a successful `SyncReport`.

## State and Persistence Behavior
The tests do not directly inspect disk files, but they rely on raft log replication/apply state. Blocking `MsgAppendResponse` prevents leader-side progress; clearing filters allows the pending entries to commit and apply. The final `SyncReport` confirms the region reached the required applied state before snapshot backup/recovery proceeds.

## Dependencies and Integration Points
The file integrates raftstore significant-message routing, async raftstore admin proposals, snapshot backup wait-apply machinery, and network filter fault injection. It depends on the test router broadcast path reaching normal peer FSMs.

## Risks
The assertions are sensitive to timing because sleeps are used to let pending admin or apply state accumulate. The covered risk is operationally important: backup snapshot recovery must not observe or report a region as safe while leader-side admin changes or log apply work are still pending.

## Test Signals
Success is signaled by `CheckPendingAdmin` responses changing from true to false, timeout while apply is blocked, and a final `SyncReport { report_id: 1, aborted: None }` after filters are cleared.
