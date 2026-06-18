# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/capture.rs

## Purpose
Implements capture-change support for applied command observation, used by CDC, resolved-ts, and PITR observers to obtain a consistent snapshot and then receive subsequent applied command batches.

## Important APIs, Types, And Functions
`PeerFsmDelegate::on_leader_callback` builds a read-index request for the current leader and routes it through query handling. `PeerFsmDelegate::on_capture_change` waits for the leader read callback and then schedules `ApplyTask::CaptureApply`. `Apply::on_capture_apply` validates observer freshness and region epoch, flushes prior writes, creates a `RegionSnapshot`, updates observe ids and observe level, and returns the snapshot. `Apply::observe_apply` records applied commands when observation is enabled. `Apply::flush_observed_apply` emits a `CmdBatch` to the coprocessor host.

## Control Flow
Capture starts on the peer FSM by issuing a leader read callback so the capture point is sequenced with raft/query state. The callback reports query errors immediately. On success it sends the capture change to the apply scheduler. Apply-side handling rejects stale observer ids, verifies the requested epoch against the current region, flushes current apply writes so the snapshot includes all prior modifications, builds the region snapshot at the current applied index, updates the requested observer id, recomputes observe level, and returns the snapshot through the callback. Later apply operations are recorded and flushed in batches to observers.

## State And Persistence Behavior
`on_capture_apply` forces an apply writebatch flush before snapshot creation. It mutates in-memory observe metadata (`cdc_id`, `rts_id`, or `pitr_id`) and observe level, but does not add raft log entries. Observed commands are buffered in memory and drained on flush; large buffers shrink back to `SHRINK_PENDING_CMD_QUEUE_CAP`.

## Dependencies And Integration Points
Depends on query read-index sequencing, apply scheduler, `ChangeObserver`, `ObserveHandle`, `ObserverType`, `RegionSnapshot`, epoch comparison, coprocessor command observation, `WriteBatchFlags::FLASHBACK`, and the router `CaptureChange` message.

## Risks And Edge Cases
Stale capture commands must be rejected or old clients could rewind observer ids. Epoch mismatch returns an error instead of a snapshot. Missing apply scheduler is converted to `RegionNotFound`. Flashback regions require a special query flag to allow capture. The snapshot must be taken after flushing prior writes, otherwise the observer could miss data before the capture point.

## Test Signals
The local `test_capture_apply` builds an apply instance, applies a put, captures, applies another put, and verifies the snapshot sees only the first put while the observer receives the second command. The `raft_on_capture_change` failpoint gives additional integration-test control.
