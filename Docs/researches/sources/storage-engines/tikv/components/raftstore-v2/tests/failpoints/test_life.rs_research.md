# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_life.rs

## Purpose
This failpoint test covers peer replacement while the old peer is stuck applying entries. It verifies that a larger peer id heartbeat can destroy the old peer, create the new peer, and survive restart even when apply progress was paused.

## Important APIs, Types, and Functions
- `test_destroy_by_larger_id_while_applying()` pauses `APPLY_COMMITTED_ENTRIES`, submits a simple write, constructs a `RaftMessage` heartbeat for the same region with a larger target peer id and higher term, and sends it through `send_raft_message`.
- It uses `assert_peer_not_exist()` and `must_query_debug_info()` to validate destruction/recreation.

## Control Flow
After the initial region applies to current term, the test pauses apply, sends a write and waits for commit, then sends a heartbeat addressed to `current_peer_id + 1` with incremented conf version and term 10. Removing the failpoint lets the system complete destruction. The test confirms the old peer disappears, debug info shows the new peer id and term, restarts the node, and checks the new peer remains.

## State and Persistence Behavior
The test validates raft peer life-cycle persistence in the raft engine while apply was interrupted. It expects the replacement peer's raft hard state term and peer id to persist across restart.

## Dependencies and Integration Points
It depends on the shared cluster harness, router write and raft-message paths, failpoint-injected apply pause, and life helper assertions.

## Risks and Edge Cases
- Larger-peer-id replacement must not be blocked forever by an applying old peer.
- Destruction must not lose the incoming higher term/hard state for the replacement peer.
- Restart must not resurrect the old peer or roll back the replacement.

## Test Signals
Assertions check old peer nonexistence, new peer `raft_status.id`, hard-state term 10, and same state after restart.
