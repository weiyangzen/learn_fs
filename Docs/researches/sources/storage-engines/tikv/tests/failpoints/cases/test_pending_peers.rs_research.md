# sources/storage-engines/tikv/tests/failpoints/cases/test_pending_peers.rs

## Purpose
This file tests PD pending-peer and store-busy reporting when snapshot apply is delayed or fails, when raft/apply state races around truncated state, and when stores have peers busy applying logs.

## Important APIs, Types, and Functions
- Tests include `test_pending_peers`, `test_pending_snapshot`, `test_on_check_busy_on_apply_peers`, and `test_on_apply_snap_failed`.
- Important helpers include `configure_for_snapshot`, `configure_for_lease_read`, `get_pending_peers`, `get_store_stats`, `must_send_store_heartbeat`, and `apply_state`.
- Failpoints include `region_apply_snap`, `apply_on_handle_snapshot_*`, `on_handle_apply_1003`, `on_mock_store_completed_target_count`, and `region_apply_snap_io_err`.

## Control Flow
The first test delays snapshot apply for a newly added peer and checks PD reports it as pending until data is applied. `test_pending_snapshot` pauses snapshot handling, isolates a peer, compacts logs to force snapshot, and checks truncated state monotonicity despite concurrent raftstore/apply writes. The busy-store test creates lag on peer 1003, restarts it with apply paused, captures append/read-index messages to confirm committed indexes, then checks store heartbeat `is_busy` under incomplete apply progress and mocked target counts. The final test injects snapshot IO error, expects the new peer to remain pending, confirms data absence, and verifies damaged region reporting in store stats.

## State and Persistence Behavior
The file observes pending peer maps in mock PD, raft apply/truncated state, store heartbeat stats, and damaged region IDs. It ensures snapshot apply progress and failures are reflected in PD-visible metadata without corrupting raft apply state.

## Dependencies and Integration Points
The tests integrate PD heartbeat/reporting, snapshot generation/application, raft message filters, apply worker failpoints, store stats, and raftstore conf changes.

## Risks and Test Signals
Risks include premature removal from pending peers, dirty writes of truncated state, false-negative store busy reports, and missing damaged-region reporting after snapshot failure. Signals are pending-peer map contents, `applied_index` comparisons, `is_busy` assertions, data presence/absence, and `damaged_regions_id` checks.
