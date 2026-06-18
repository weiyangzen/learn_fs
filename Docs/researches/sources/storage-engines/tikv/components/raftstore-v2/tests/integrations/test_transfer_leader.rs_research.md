# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_transfer_leader.rs

## Purpose
This file validates leader transfer in a multi-node raftstore-v2 cluster with real replication dispatch. It ensures followers catch up before transfer, leadership is observed consistently on both source and target routers, and writes work before and after transfer in both directions.

## Important APIs, Types, and Functions
- `put_data()` writes a key through a specified leader node, dispatches messages in phases, verifies local visibility, verifies follower lag before heartbeat, then triggers raft ticks to commit on follower and verifies follower visibility.
- `must_transfer_leader()` sends `AdminCmdType::TransferLeader`, then loops dispatching messages and querying debug info until both routers report the target leader id.
- `test_transfer_leader()` creates a three-node cluster, adds node 1 as a voter, writes data, transfers leadership to node 1, writes again, and transfers back to node 0.

## Control Flow
The test first adds a peer with `ConfChangeType::AddNode`, dispatches to create it, and validates follower debug info. `put_data()` drives proposal/commit by sleeps plus `cluster.dispatch()` and explicit raft ticks. Transfer leader uses admin command plus repeated dispatch and debug polling with a final assert fallback.

## State and Persistence Behavior
The test mutates replicated tablet data and raft leadership state. It observes follower snapshots before and after commit heartbeats to ensure data application follows raft commit, not just message receipt.

## Dependencies and Integration Points
It integrates cluster multi-node setup, conf-change admin commands, transfer-leader admin commands, raft ticks, dispatch transport simulation, stale snapshots, and debug metadata.

## Risks and Edge Cases
- Transfer to a lagging follower should be preceded by data catch-up; the helper explicitly tests commit propagation.
- Leadership observations must converge on both old and new leader routers.
- Writes after transfer must use the new leader and still replicate back.

## Test Signals
Signals include successful add-node metadata, follower leader id, key visibility on leader and later follower, transfer command success, and both routers reporting the expected leader id in debug info.
