# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_life.rs

## Purpose
This file tests raftstore-v2 peer life-cycle behavior driven by raft messages, tombstone messages, larger peer ids, GC peer requests/responses, and removed-peer record cleanup.

## Important APIs, Types, and Functions
- `test_life_by_message()` verifies valid raft messages create uninitialized peers, invalid messages do not, peers survive restart, and tombstone messages destroy/persist tombstones.
- `test_destroy_by_larger_id()` validates larger target peer id replacement, smaller peer id ignore/report behavior, and restart survival.
- `test_gc_peer_request()` ensures tombstone messages create-and-destroy unknown peers, prevent later normal recreation, and report on repeated tombstones.
- `test_gc_peer_response()` verifies leader-side tombstone messages for removed peers on vote/pre-vote and GC ticks, follower-side GC response reporting, and removed-record cleanup after a later write.

## Control Flow
The tests craft `RaftMessage` instances manually, mutate store id/epoch/tombstone flags/msg types, send them through routers, and observe debug info or transport receivers. Multi-node GC tests add and remove a learner, drain messages, send vote messages from the removed peer, forward tombstone messages to the removed node, then feed GC reports back to the leader and trigger record cleanup with a tick plus write.

## State and Persistence Behavior
They inspect raft state, apply state, region local state, tombstone markers, removed records, hard-state term, and restart survival. Tombstone persistence is validated with direct raft-engine debug helpers.

## Dependencies and Integration Points
The file uses cluster life helpers, raft message types, raft conf changes, router ticks, raft-engine read-only/debug APIs, and simple writes.

## Risks and Edge Cases
- Invalid peer creation messages must be ignored without partial persistent state.
- Tombstone messages must both destroy existing peers and prevent recreation by later stale normal messages.
- Larger peer id replacement must not lose term or leave old peer runnable.
- Removed-peer GC must avoid endless vote traffic while eventually pruning removed records.

## Test Signals
Signals include peer nonexistence, persisted tombstone state, heartbeat response/absence, GC peer response messages, tombstone outbound messages, removed-record length, and post-write cleanup.
