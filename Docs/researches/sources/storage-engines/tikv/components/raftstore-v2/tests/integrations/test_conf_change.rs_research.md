# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_conf_change.rs

## Purpose
This file validates raftstore-v2 configuration-change behavior: adding learners, snapshot catch-up, removing peers, repeated peer recreation cleanup, removal with concurrent replicated writes, and responses to unknown peers.

## Important APIs, Types, and Functions
- `test_simple_change()` adds a learner, writes data after snapshot, verifies learner truncated/applied state and data, removes it, repeats add/remove cycles, and checks WAL skipping for admin commands.
- `test_remove_by_conf_change()` sends remove-peer and write messages together so the learner receives removal and later log entries, then verifies tombstone state and raft state cleanup.
- `add_learner()`, `write_kv()`, and `remove_peer()` are local helper functions for conf-change admin requests and replication dispatch.
- `test_unknown_peer()` sends a heartbeat from an unknown peer and expects a heartbeat response, proving peer cache/liveness behavior.

## Control Flow
Add learner uses `AdminCmdType::ChangePeer` with `AddLearnerNode`, validates leader metadata, dispatches heartbeat/snapshot messages to create the learner, and waits for snapshot generation. Removal sends `RemoveNode`, ticks raft on the removed peer, dispatches messages, sleeps for apply, and checks raft-engine tombstone state. Unknown-peer testing sends a fake heartbeat with matching target peer/epoch but unknown sender and reads the transport receiver for a heartbeat response.

## State and Persistence Behavior
The tests inspect raft-engine region state, tombstone state, raft state removal, applied/truncated indexes, tablet snapshots, and WAL files. They verify removed peers are persisted as tombstones and raft state is cleared.

## Dependencies and Integration Points
They use cluster dispatch/snapshot simulation, raft `ConfChangeType`, raft-engine read-only APIs, `PeerTick::Raft`, `SimpleWriteEncoder`, and life-cycle paths that create/destroy peers from raft messages.

## Risks and Edge Cases
- Learner snapshot apply must set truncated index equal to leader match index and preserve newly written data.
- Removing a peer must tolerate later replicated entries without resurrecting raft state.
- Repeated add/remove of peer ids must not leave stale registry or raft-engine state.
- Unknown peer responses are necessary for conf-change liveness.

## Test Signals
Signals include debug metadata peer lists/epochs, learner snapshot reads, `PeerState::Tombstone`, `get_raft_state == None`, heartbeat response messages, and empty WAL verification.
